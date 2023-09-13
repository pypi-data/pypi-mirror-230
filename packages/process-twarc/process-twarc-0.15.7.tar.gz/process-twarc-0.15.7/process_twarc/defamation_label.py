from transformers import DataCollatorWithPadding, AutoModelForSequenceClassification, TrainingArguments, Trainer, TrainerCallback, EarlyStoppingCallback, get_constant_schedule, get_linear_schedule_with_warmup
from process_twarc.util import load_tokenizer, load_dataset, load_dict
from process_twarc.preprocess import generate_splits
import torch
import evaluate 
import numpy as np
import wandb
import optuna
from torch.optim import AdamW

def defamation_label_sweep(
    path_to_data: str,
    path_to_tokenizer: str,
    path_to_model: str,
    checkpoint_dir: str,
    path_to_search_space: str,
    path_to_storage: str,
    n_trials: int=10,
    enable_pruning: bool=False,
    print_details: bool=True,
    report_to: str="wandb"
):
    search_space = load_dict(path_to_search_space)
    project = search_space["meta"]["project"]
    group = search_space["meta"]["wandb_group"]
    study_name = search_space["meta"]["optuna_study"]
    raw_datasets = load_dataset(path_to_data, output_type="Dataset")
    tokenizer = load_tokenizer(path_to_tokenizer)
    tokenized_datasets = raw_datasets.map(lambda example: tokenizer(example["text"]))

    splits = generate_splits(
        tokenized_datasets,
        test_size=0.15,
        validation_size=0.10,
        development_size=0.15)
    
    train_dataset = splits["train"]
    eval_dataset = splits["validation"]
    test_dataset = splits["development"]

    def objective(trial):
    
        trial_number = str(trial.number+1).zfill(3)
        trial_dir = f"{checkpoint_dir}/{study_name}/trial{trial_number}"
        run_name = f"{group}-{trial_number}"

        def suggest_parameter(param_name):

            param_space = search_space[param_name]
            dtype = param_space["type"]
            if dtype == "categorical":
                return trial.suggest_categorical(
                    name=param_name,
                    choices=param_space["choices"])
            elif dtype == "int":
                suggest = trial.suggest_int
            elif dtype == "float":
                suggest = trial.suggest_float
            if "step" in param_space.keys():
                return suggest(
                    name=param_name,
                    low=param_space["low"],
                    high=param_space["high"],
                    step=param_space["step"]
                )
            elif "log" in param_space.keys():
                return suggest(
                    name=param_name,
                    low=param_space["low"],
                    high=param_space["high"],
                    log=param_space["log"]
                )
            else:
                return suggest(
                    name=param_name,
                    low=param_space["low"],
                    high=param_space["high"]
                )
        #Variable Params
        learning_rate = suggest_parameter("learning_rate")
        hidden_dropout_prob = suggest_parameter("hidden_dropout_prob")
        attention_dropout_prob = suggest_parameter("attention_dropout_prob")
        weight_decay = suggest_parameter("weight_decay")

        #Fixed Params
        LR_SCHEDULER_TYPE = "constant"
        NUM_TRAIN_EPOCHS = 15
        PATIENCE = 3
        ADAM_BETA1 = 0.9
        ADAM_BETA2 = 0.999
        ADAM_EPSILON = 1e-8
        PER_DEVICE_TRAIN_BATCH_SIZE = 20
        PER_DEVICE_EVAL_BATCH_SIZE = 30
        NUM_LABELS = 4
        ID2LABEL = {
            0: "B1",
            1: "B2",
            2: "B3",
            3: "B4"
        }
        LABEL2ID = {
            "B1": 0,
            "B2": 1,
            "B3": 2,
            "B4": 3
        }


        fixed_params = {
            "lr_scheduler_type": LR_SCHEDULER_TYPE,
            "adam_beta1": ADAM_BETA1,
            "adam_beta2": ADAM_BETA2,
            "adam_epsilon": ADAM_EPSILON,
            "per_device_train_batch_size": PER_DEVICE_TRAIN_BATCH_SIZE,
            "per_device_eval_batch_size": PER_DEVICE_EVAL_BATCH_SIZE,
            "num_labels": NUM_LABELS,
            "id2label": ID2LABEL,
            "label2id": LABEL2ID}

        variable_params = {
            "learning_rate": learning_rate,
            "attention_dropout_prob": attention_dropout_prob,
            "hidden_dropout_prob": hidden_dropout_prob,
            "weight_decay": weight_decay
        }

        wandb.init(
            project=project,
            group=group,
            name=run_name,
            entity="lonewolfgang",
            config ={
            "meta": {
                "path_to_tokenizer": path_to_tokenizer,
                "path_to_model": path_to_model
                },
            "model":{
                "model_type": "bert",
                "hidden_act": "gelu",
                "hidden_size": 768,
                "num_hidden_layers": 12,
                "intermediate_size": 3072,
                "num_attention_heads": 12,
                "max_position_embeddings": 512,
                "position_embedding_type": "absolute",
                "vocab_size": 32_003,
                "initializer_range": 0.02,
                "attention_dropout_prob": attention_dropout_prob,
                "hidden_dropout_prob": hidden_dropout_prob,
                "weight_decay": weight_decay,
                "layer_norm_eps": 1e-12,
            },
            "optimizer":{
                "optim": "adamw_hf",
                "lr_scheduler_type": LR_SCHEDULER_TYPE,
                "learning_rate": learning_rate,
                "adam_beta1": ADAM_BETA1,
                "adam_beta2": ADAM_BETA2,
                "adam_epsilon": ADAM_EPSILON,
            },
            "trainer": {
                "num_train_epochs": NUM_TRAIN_EPOCHS,
                "logging_strategy": "steps",
                "logging_steps": 5,
                "per_device_eval_batch_size": PER_DEVICE_EVAL_BATCH_SIZE,
                "per_device_train_batch_size": PER_DEVICE_TRAIN_BATCH_SIZE,
                "eval_strategy": "steps",
                "eval_steps": 31_912,
                "save_strategy": "steps",
                "save_steps": 31_912,
                "metric_for_best_model": "eval_loss",
                "seed": 42
            }}, 
            reinit=True
            )

        if print_details:
            print("\nVariable Params:")
            for key in variable_params:
                print(key, variable_params[key])
            print("\nFixed Params:")
            for key in fixed_params:
                print(key, fixed_params[key])
    
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model = AutoModelForSequenceClassification.from_pretrained(
            path_to_model,
            num_labels=NUM_LABELS,
            id2label=ID2LABEL,
            label2id=LABEL2ID   
        ).to(device)

        optimizer = AdamW(
            params=model.parameters(),
            lr=learning_rate,
            betas = (ADAM_BETA1, ADAM_BETA2),
            eps=ADAM_EPSILON,
            weight_decay=weight_decay)
        

        scheduler = get_constant_schedule(
            optimizer=optimizer)

        data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

        def compute_metrics(eval_pred):
            accuracy = evaluate.load("accuracy")
            predictions, labels = eval_pred
            predictions = np.argmax(predictions, axis=1)
            return accuracy.compute(predictions=predictions, references=labels)
        
        training_args = TrainingArguments(
            learning_rate=learning_rate,
            lr_scheduler_type=LR_SCHEDULER_TYPE,
            adam_beta1=ADAM_BETA1,
            adam_beta2=ADAM_BETA2,
            adam_epsilon=ADAM_EPSILON,
            weight_decay=weight_decay,
            output_dir=trial_dir,
            logging_steps=5,
            evaluation_strategy="epoch",
            eval_steps=1,
            save_strategy="epoch",
            save_steps=1,
            metric_for_best_model="eval_accuracy",
            save_total_limit=3,
            load_best_model_at_end=True,
            push_to_hub=False,
            per_device_train_batch_size=PER_DEVICE_TRAIN_BATCH_SIZE,
            per_device_eval_batch_size=PER_DEVICE_EVAL_BATCH_SIZE,
            num_train_epochs=NUM_TRAIN_EPOCHS,
            report_to=report_to)
        
        class OptunaCallback(TrainerCallback):
            def __init__(self, trial, should_prune=True):
                self.trial = trial
                self.should_prune = should_prune

            def on_evaluate(self, args, state, control, metrics=None, **kwargs):
                eval_loss = metrics.get("eval_loss")
                self.trial.report(eval_loss, step=state.global_step)
                if self.should_prune and self.trial.should_prune():
                    raise optuna.TrialPruned()

        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            data_collator=data_collator,
            compute_metrics=compute_metrics,
            optimizers=(optimizer, scheduler),
            callbacks=[
                OptunaCallback(trial, should_prune=enable_pruning),
                EarlyStoppingCallback(early_stopping_patience=PATIENCE)]
        )

        trainer.train()
        results = trainer.evaluate(test_dataset)
        wandb.log(results)
        trainer.save_model(trial_dir)

        return results["eval_accuracy"]
    
    study_name = search_space["meta"]["optuna_study"]
    study = optuna.create_study(
        storage=path_to_storage,
        pruner=optuna.pruners.MedianPruner(n_warmup_steps=5, interval_steps=3, n_min_trials=10),
        study_name=study_name,
        direction="maximize",
        load_if_exists=True,
        )
    study.optimize(objective, n_trials=n_trials)
