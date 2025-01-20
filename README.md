# klipper-auto-can-scanner

## 0. 目的と原理

### 0.1 目的

- CANバスを使用するKlipperシステムで、ツールヘッドのCANボードを入れ替える際に、新しいボードのCAN UUIDを自動認識させるためのプログラムです。

### 0.2 原理
- 本プログラムは、systemdのサービスとして登録されます。デバイスを起動する際に一度だけ自動実行します(デフォルトは無効)。また、<code>mainsail UIの「system/service」</code>から強制実行こともできます。
- 本プログラムはCAN UUIDスキャンを実行し、メインMCUに指定されたUUID以外がスキャンされた場合、そのUUIDを<code>deviceConfigName</code>で指定された設定項目名の<code>canbus_uuid</code>に代入します。
- ※<code>2つ以上</code>のUUIDがスキャンされる場合、どれを使用するか特定できないため、本プログラムは異常状態で終了します。

## 1. インストール
<pre>
cd ~
git clone https://github.com/ChipCE/klipper-auto-can-scanner
cd klipper-auto-can-scanner
chmod +x ./install.sh
sudo ./install.sh
</pre>

## 2. 設定ファイル
<pre>
{
  "scannerPath" : "./scan.sh",
  "scanTimeout" : 3,
  "klipperConfigFile": "/home/pi/klipper_config/printer.cfg",
  "restartKlipper": true,
  "deviceConfigName": "mcu myCanDevice",
  "blackList": [],
  "whiteList": []
}
</pre>

- <code>scannerPath</code> : CANスキャンコマンドを呼び出すスクリプトファイル。基本は変更不要。(例:"./scan.sh")
- <code>scanTimeout</code> : CANスキャンの最大時間。(単位:秒)、(例:3)
- <code>klipperConfigFile</code> : printer.cfgのパス。(例:"/home/pi/klipper_config/printer.cfg")
- <code>restartKlipper</code> : 設定を変更した後、klipperを再起動させるかどうか。(例:true/false)
- <code>deviceConfigName</code> : printer.cfgに指定されたツールヘッドの設定項目名。(例:mcu myCanDevice)
- <code>blackList</code> : ブラックリスト。ここに記載されたUUIDをスキップする。(例:["uuid1","uuid2"])
- <code>whiteList</code> : ホワイトリスト。ここに記載されたUUIDのみ使用する。記載しない場合は全て使用可。(例:["uuid1","uuid2"])

## 3. ログファイル

ログファイル : <code>~/klipper-auto-can-scanner/klipper-auto-can-scanner.log</code>

## 4. UI

## 5. 注意

- 本プログラムは<code>configparser</code>でKlipper設定ファイルの管理を行うため、設定ファイルのコメントは無視されます。コメントを使用する場合、インラインコメントを使用すること。

例
<pre>
# motor 1 port ←　このコメントは無視されて、設定を上書きする際、なくなります。
[stepper_y]
step_pin: PG  ; port 1 step pin ←　このコメントは残ります。
dir_pin: !PG1
enable_pin: !PF15
...
</pre>

## 6. ライセンス
本プログラムは、[Klipper](https://github.com/Klipper3d/klipper)（GPL-3.0ライセンス）のコードを使用しているため、同じライセンス体制でコードの公開が義務付けられます。詳細については[ライセンスを確認](./LICENSE)してください。