
from transformers import Trainer, AutoTokenizer, AutoModelForMaskedLM, TrainingArguments, DataCollatorForLanguageModeling, TrainerCallback, EarlyStoppingCallback, get_linear_schedule_with_warmup
from torch.optim import AdamW
from torch.utils.data import DataLoader
from process_twarc.util import  load_dict, load_tokenizer, get_all_files, load_dataset
from process_twarc.preprocess import tokenize_for_masked_language_modeling
import torch
import wandb
import optuna
from ntpath import basename

def MLM_sweep(
    data_dir: str,
    path_to_tokenizer: str,
    path_to_model: str,
    checkpoint_dir: str,
    path_to_search_space: str,
    path_to_storage: str,
    n_trials: int=1,
    enable_pruning: bool=False,
    push_to_hub: bool=False,
    print_details: bool=True,
    report_to: str="wandb"
):

    search_space = load_dict(path_to_search_space)

    base = lambda file_path: basename(file_path).split(".")[0]
    split_paths = [path for path in get_all_files(data_dir) if base(path) != "test"]
    raw_datasets = {k:v for k,v in zip(
        [base(path) for path in split_paths],
        [load_dataset(path) for path in split_paths]
    )}

    tokenizer = load_tokenizer(path_to_tokenizer, AutoTokenizer, print_details=print_details)
    tokenized_datasets = {k:tokenize_for_masked_language_modeling(v, tokenizer) for k,v in raw_datasets.items()}

    train_dataset = tokenized_datasets["train"]
    eval_dataset = tokenized_datasets["validation"]
    test_dataset = tokenized_datasets["development"]

    def objective(trial):

        trial_number = str(trial.number+1).zfill(3)
        project = search_space["meta"]["project"]
        group = search_space["meta"]["wandb_group"]
        study_name = search_space["meta"]["optuna_study"]
        trial_dir = f"{checkpoint_dir}/{study_name}/trial{trial_number}"
        run_name = f"{study_name}-{trial_number}"

        def suggest_parameter(param_name):

            param_space = search_space[param_name]
            dtype = param_space["type"]
            if dtype == "categorical":
                return trial.suggest_categorical(
                    name=param_name,
                    choices=param_space["choices"])
            elif dtype == "int":
                suggest_method = trial.suggest_int
            elif dtype == "float":
                suggest_method = trial.suggest_float
            if "step" in param_space.keys():
                    return suggest_method(
                        name=param_name,
                        low=param_space["low"],
                        high=param_space["high"],
                        step=param_space["step"]
                    )
            elif "log" in param_space.keys():
                return suggest_method(
                    name=param_name,
                    low=param_space["low"],
                    high=param_space["high"],
                    log=param_space["log"]
                )
            else:
                return suggest_method(
                    name=param_name,
                    low=param_space["low"],
                    high=param_space["high"]
                )
        #Fixed Parameters
        PER_DEVICE_TRAIN_BATCH_SIZE = 55
        PER_DEVICE_EVAL_BATCH_SIZE = 75
        INTERVAL = 12
        EVAL_STRATEGY = "steps"
        SAVE_STRATEGY = "steps"
        METRIC_FOR_BEST_MODEL = "eval_loss"
        PATIENCE = 3
        SEED = 42

        
        #Variable Parameters
        hidden_dropout_prob=suggest_parameter("hidden_dropout_prob")
        attention_dropout_prob=suggest_parameter("attention_dropout_prob")
        do_weight_decay=suggest_parameter("do_weight_decay")
        if do_weight_decay == True:
            weight_decay=suggest_parameter("weight_decay")
        else:
            weight_decay=0.0
        num_train_epochs=suggest_parameter("num_train_epochs")
        initial_learning_rate=suggest_parameter("initial_learning_rate")
        num_warmup_steps=suggest_parameter("num_warmup_steps")
        power=suggest_parameter("power")
        adam_beta1=suggest_parameter("adam_beta1")
        adam_beta2=suggest_parameter("adam_beta2")
        adam_epsilon=suggest_parameter("adam_epsilon")

        wandb.init(
            project=project,
            group=group,  
            entity="lonewolfgang",
            name=run_name,
            config ={
            "meta": {
                "_name_or_path": "LoneWolfgang/bert-for-japanese-twitter"},
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
                "lr_scheduler_type": "linear",
                "initial_learning_rate": initial_learning_rate,
                "num_warmup_steps": num_warmup_steps,
                "adam_beta1": adam_beta1,
                "adam_beta2": adam_beta2,
                "adam_epsilon": adam_epsilon,
            },
            "trainer": {
                "num_train_epochs": num_train_epochs,
                "logging_strategy": "steps",
                "logging_steps": 500,
                "per_device_eval_batch_size": PER_DEVICE_EVAL_BATCH_SIZE,
                "per_device_train_batch_size": PER_DEVICE_TRAIN_BATCH_SIZE,
                "eval_strategy": EVAL_STRATEGY,
                "eval_steps": 31_912,
                "save_strategy": SAVE_STRATEGY,
                "save_steps": 31_912,
                "patience": PATIENCE,
                "save_total_limit": INTERVAL,
                "metric_for_best_model": METRIC_FOR_BEST_MODEL,
                "seed": SEED
            }
        })

        fixed_params = {
            "per_device_train_batch_size": PER_DEVICE_TRAIN_BATCH_SIZE,
            "per_device_eval_batch_size": PER_DEVICE_EVAL_BATCH_SIZE
        }

        variable_params = {
            "hidden_dropout_prob": hidden_dropout_prob,
            "attention_dropout_prob": attention_dropout_prob,
            "weight_decay": weight_decay,
            "num_train_epochs": num_train_epochs,
            "initial_learning_rate": initial_learning_rate,
            "num_warmup_steps": num_warmup_steps,
            "power": power,
            "adam_beta1": adam_beta1,
            "adam_beta2": adam_beta2,
            "adam_epsilon": adam_epsilon
        }
    
        print("\nVariable Params:")
        for key in variable_params:
            print(key, variable_params[key])
        print("\nFixed Params:")
        for key in fixed_params:
            print(key, fixed_params[key])


        def collate_data(collator_class, tokenizer, tokenized_dataset, per_device_train_batch_size, print_details=print_details):
            data_collator = collator_class(tokenizer)
            train_dataloader = DataLoader(
                tokenized_dataset,
                batch_size=per_device_train_batch_size,
                shuffle=True,
                collate_fn=data_collator
            )
            if print_details:
                print("Data collated.")
                print(f"\nBatch Size: {per_device_train_batch_size}")
                print("Shape of first five batches:")
                for step, batch in enumerate(train_dataloader):
                    print(batch["input_ids"].shape)
                    if step > 5:
                        break
            return data_collator

        device = "cuda" if torch.cuda.is_available() else RuntimeError("No GPU available.")

        tokenizer = load_tokenizer(path_to_tokenizer, AutoTokenizer, print_details=print_details)
        model = AutoModelForMaskedLM.from_pretrained(
            path_to_model,
            hidden_dropout_prob=hidden_dropout_prob,
            attention_dropout_prob=attention_dropout_prob).to(device)
        if print_details:
            print(model.config)

        data_collator = collate_data(DataCollatorForLanguageModeling, tokenizer, train_dataset, PER_DEVICE_TRAIN_BATCH_SIZE)

        optimizer = AdamW(
            params=model.parameters(),
            lr=initial_learning_rate,
            betas = (adam_beta1, adam_beta2),
            eps=adam_epsilon,
            weight_decay=weight_decay)
        
        scheduler = get_linear_schedule_with_warmup(
            optimizer=optimizer,
            num_warmup_steps=num_warmup_steps,
            num_training_steps=len(train_dataset)//PER_DEVICE_TRAIN_BATCH_SIZE * num_train_epochs
        )

        training_args = TrainingArguments(
            lr_scheduler_type="linear",
            learning_rate=initial_learning_rate,
            adam_beta1=adam_beta1,
            adam_beta2=adam_beta2,
            adam_epsilon=adam_epsilon,
            weight_decay=weight_decay,
            output_dir=trial_dir,
            evaluation_strategy=EVAL_STRATEGY,
            eval_steps= 1 / INTERVAL / num_train_epochs,
            num_train_epochs=num_train_epochs,
            save_strategy=SAVE_STRATEGY,
            save_steps=1 / INTERVAL /num_train_epochs,
            save_total_limit=INTERVAL,
            push_to_hub=push_to_hub,
            per_device_train_batch_size=PER_DEVICE_TRAIN_BATCH_SIZE,
            per_device_eval_batch_size=PER_DEVICE_EVAL_BATCH_SIZE,
            load_best_model_at_end=True, 
            metric_for_best_model=METRIC_FOR_BEST_MODEL,
            report_to=report_to
        )

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
            data_collator=data_collator,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            tokenizer=tokenizer,
            optimizers=(optimizer, scheduler),
            callbacks=[EarlyStoppingCallback(early_stopping_patience=PATIENCE),
                       OptunaCallback(trial, should_prune=enable_pruning)]
        )
        trainer.train()
        results = trainer.evaluate(test_dataset)
        print("\nResults:", results)
        wandb.log(results)
        trainer.save_model()

        return results["eval_loss"]
    
    study_name = search_space["meta"]["optuna_study"]
    study = optuna.create_study(
        storage=path_to_storage,
        pruner=optuna.pruners.MedianPruner(n_warmup_steps=6, interval_steps=3),
        study_name=study_name,
        direction="minimize",
        load_if_exists=True,
        )
    study.optimize(objective, n_trials=n_trials)
