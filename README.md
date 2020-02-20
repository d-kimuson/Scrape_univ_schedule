# 会津大学 スケジュールスクレイピング

## 環境

```shell script
$ sw_vers
ProductName:    Mac OS X
ProductVersion: 10.15.3
BuildVersion:   19D76
```

## Setup

### 1. .envファイル, credentiaals.json の準備

- .env.sample ファイルを参考に, ログイン情報を .env ファイル に書き, src 下に設置
- [Python Quickstart - Google Calnder API](https://developers.google.com/calendar/quickstart/python?hl=ja) から credentiaals.json をダウンロードして設置

### 2. 環境構築

```shell script
$ pip install pipenv
$ pipenv install --dev --ignore-pipfile
$ pipenv shell
```

### 3. 実行

```shell script
$ pipenv run start
```
