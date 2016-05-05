# Ansible SSH wrapper

Handy tools for everyone using ansible for accessing host defined in your inventory.

```
$ ansible-ssh [host] [any ssh-arguments]
```

Ansible-ssh will parse all available inventory files and tries to find host passed as first argument.
It will then execute ssh host.

## Instalation

Just copy ansible-ssh.py in to your PATH and make it executable.