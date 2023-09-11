# sumake
## use
```
pip install sumake -U
```


## dev
make install

pip install . 

## zsh
 ~/.zshrc

```bash
autoload -U compinit
compinit
_sumake() {
_make "$@"
}
compdef _sumake sumake
zstyle ':completion::complete:sumake:*:targets' call-command true
```
