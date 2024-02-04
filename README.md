# stable-diffusion-API

API using [Stability-AI/stability-sdk](https://github.com/Stability-AI/stability-sdk).

## Getting Started

### Prepare

```
#### on macOS
download .env from https://drive.google.com/file/d/18dR3H-CY4tezkiQXwsF6XKOxoZde1Ztd/view?usp=drive_link
```

## Run on Local

```
$ python3 -m venv pyenv
$ source pyenv/bin/activate
$ pyenv/bin/pip3 install -r requirements.txt

$ flask run -p 8000
```
別のターミナルウィンドを開く
$ python3 -m http.server 80 -d stable-diffusion-API/test   
Go to http://localhost

## Run on Docker

```
$ docker build --platform linux/amd64 ./ -t sdapi
docker desktopからimages -> sdapi -> runPorts Local Host 8000
```
別のターミナルウィンドを開く
$ python3 -m http.server 80 -d stable-diffusion-API/test
Go to http://localhost

## 本番化
```
AWSコンソールのAmazon Elastic Container Registryでプッシュコマンド表示
https://ap-northeast-1.console.aws.amazon.com/ecr/repositories/private/063950159980/sdapi?region=ap-northeast-1
表示の通りコマンド実行
コンテナのアップが完了したら、EC2再起動
```
