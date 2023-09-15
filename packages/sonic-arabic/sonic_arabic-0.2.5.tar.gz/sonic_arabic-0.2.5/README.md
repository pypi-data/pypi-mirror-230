## Установка
```
# on Ubuntu or Debian
sudo apt update && sudo apt install ffmpeg cmake libboost-all-dev

# on MacOS using Homebrew (https://brew.sh/)
brew install ffmpeg cmake boost

pip install sonic_arabic
```

## Пример запуска
```
from sonic_arabic.audio_pipeline import AudioAnalysisPipeline

path_audio_file = 'data/arabic_1m.m4a'
analyzer = AudioAnalysisPipeline()
result = analyzer.predict(path_audio_file)
print(result['ner'])
print(result['sentiment'])
print(result['punctuation'])
```