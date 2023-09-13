import json
from pathlib import Path
from typing import Union

from vatis.asr_commons.domain.models_config import TranscriptionConfig, ModelConfig, LanguageConfig

DEFAULT_TRANSCRIPTION_CONFIG_PATH: Path = Path('/var/lib/vatis/transcription-config/transcription-config.json')


def read(config_path: Union[str, Path] = DEFAULT_TRANSCRIPTION_CONFIG_PATH,
         throw_on_error: bool = False) -> TranscriptionConfig:
    try:
        with open(config_path, 'r') as f:
            config_data = f.read()
            config_json = json.loads(config_data)

            return TranscriptionConfig.from_json(config_json)
    except Exception as e:
        if not throw_on_error:
            return TranscriptionConfig(languageConfigs=[])
        else:
            raise e


def write(transcription_config: TranscriptionConfig, config_path: Union[str, Path] = DEFAULT_TRANSCRIPTION_CONFIG_PATH):
    config_path = Path(config_path)

    if not config_path.parent.exists():
        config_path.parent.mkdir(parents=True, exist_ok=True)

    with open(config_path, 'w') as f:
        config_json = transcription_config.to_json()
        config_data = json.dumps(config_json)

        f.write(config_data)


def update_model_config(model_config: ModelConfig,
                        add_new_language_if_not_exists: bool = True,
                        config_path: Union[str, Path] = DEFAULT_TRANSCRIPTION_CONFIG_PATH) -> TranscriptionConfig:
    transcription_config: TranscriptionConfig = read(config_path)
    language_exists: bool = False

    for language_config in transcription_config.languageConfigs:
        if language_config.language == model_config.language:
            language_exists = True

            i: int = 0
            for i in range(len(language_config.models)):
                if language_config.models[i].uid == model_config.uid:
                    break

            if i == len(language_config.models):
                language_config.models.append(model_config)
            else:
                language_config.models[i] = model_config
            break

    if not language_exists and add_new_language_if_not_exists:
        language_config = LanguageConfig(language=model_config.language,
                                         default=False,
                                         models=[model_config])
        transcription_config.languageConfigs.append(language_config)

    write(transcription_config, config_path)

    return transcription_config


def get_model_config(uid: str, config_path: Union[str, Path] = DEFAULT_TRANSCRIPTION_CONFIG_PATH) -> ModelConfig:
    transcription_config: TranscriptionConfig = read(config_path)

    for language_config in transcription_config.languageConfigs:
        for model_config in language_config.models:
            if model_config.uid == uid:
                return model_config
