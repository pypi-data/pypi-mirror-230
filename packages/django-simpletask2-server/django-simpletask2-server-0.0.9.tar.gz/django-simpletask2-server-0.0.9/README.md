# django-simpletask2-server

配合django-simpletask2使用的服务器程序。启动后，能自动处理django-simpletask2生成的异步处理任务。

## 安装

```
pip install django-simpletask2-server
```

## 使用

```
test@test django-simpletask2-server % django-simpletask2-server --help
Usage: django-simpletask2-server [OPTIONS] COMMAND [ARGS]...

Options:
  --logfmt TEXT
  --logfile TEXT
  --loglevel TEXT
  --pidfile TEXT                  pidfile file path.
  --workspace TEXT                Set running folder
  --daemon / --no-daemon          Run application in background or in
                                  foreground.
  -c, --config TEXT               Config file path. Application will search
                                  config file if this option is missing. Use
                                  sub-command show-config-fileapaths to get
                                  the searching tactics.
  --error-sleep INTEGER
  --idle-sleep INTEGER
  -t, --threads INTEGER
  --auto-reset-task-interval INTEGER
  --do-auto-reset-task / --no-do-auto-reset-task
  --task-pull-timeout INTEGER
  --task-pull-engine TEXT
  --channel-flags-template TEXT
  --channel-name-strip-regex TEXT
  --channel-name-template TEXT
  --channels TEXT
  -r, --redis TEXT
  -a, --aclkey TEXT
  -s, --server TEXT
  --help                          Show this message and exit.

Commands:
  restart                Restart Daemon application.
  show-config-filepaths  Print out the config searching paths.
  show-configs           Print out the final config items.
  start                  Start daemon application.
  stop                   Stop daemon application.


```

## 应用程序配置项

- server: 必要参数。默认为http://127.0.0.1:8000/django-simpletask2/。
- aclkey: 必要参数。无默认。
- redis: 当task-pull-engine为redis时，该项为必填参数。使用格式：redis://:password@redis-server:redis-port/redis-db?decode_responses=True（选项decode_responses为必要参数）。
- channels: 必要参数。默认为default.
- threads: 必要参数。默认为1
- task-pull-engine 必要参数。默认为redis。其它可选有：api。
- idle_sleep: 默认为5（秒）。
- error_sleep: 默认为5（秒）。
- 其它可选项如：logdevel, logfile, logfmt, workspace, pidfile, daemon等等，详见应用`daemon-application`。

## 版本历史

### v0.0.6

- 初始版本。

### v0.0.7

- 修正--channels短参数冲突问题。

### v0.0.8

- 文档更新。

### v0.0.9

- 文档更新。
