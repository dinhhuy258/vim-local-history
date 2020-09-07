# vim-local-history

## Introduction

A Neovim plugin for maintaining local history of files.
![](https://user-images.githubusercontent.com/17776979/91653510-d7eb3c80-eacb-11ea-864d-457e0a8e0b61.png)

Every time you save a file, a copy of the saved contents is kept in the local history. At any time, you can compare a file with any older version from the history. It can help you out when you change a file by accident. The file revision is stored inside the `.local-history` folder of your workspace directory (you can also configure another location)

## Requirements

- Neovim (vim is not supported)
- Python 3.7

## Install

Install pynvim

```sh
pip3 install pynvim
```

Install Neovim plugin

```VimL
Plug 'dinhhuy258/vim-local-history', {'branch': 'master', 'do': ':UpdateRemotePlugins'}
```

## Usage

Use command `LocalHistoryToggle` to open/close local history.

You can map this command to another key:

```VimL
nnoremap <F5> :LocalHistoryToggle<CR>
```

If you see an error `Not and editor command: LocalHistoryToggle`  you need to run `:UpdateRemotePlugins`
If the error still occurs, run the following command

```sh
pip install --user --upgrade pynvim
```

then restart nvim and re-run `:UpdateRemotePlugins` and finally restart nvim, `:LocalHistoryToggle` will exist

## Key bindings

These functions are only work under the `LocalHistory` buffer.

| Functions | Usage | Default keys |
|-----------|-------|--------------|
| move_older | Navigate to older change | `j` |
| move_newer | Navigate to newer change | `k` |
| move_oldest | Navigate to the oldest change | `G` |
| move_newest | Navigate to the newest change | `gg` |
| revert | Revert to selected change | `Enter` |
| diff | Vertical diff of current buffer with selected change | `r` |
| delete | Delete selected change | `d` |
| bigger | Increase local history graph size | `L` |
| smaller | Decrease local history graph size | `H` |
| preview_bigger | Increase local history preview size | `K` |
| preview_smaller | Decrease local history preview size | `J` |
| quit | Close local history windows | `q` |

## Configuration

You can tweak the behavior of LocalHistory by setting a few variables in your vim setting file. For example:

```VimL
let g:local_history_path = '/Users/dinhhuy258/.local-history'
let g:local_history_max_changes = 100
...
```

### g:local_history_enabled

Disable/ enable local history

Possible values:
- `0`: Never (Disable local history plugin)
- `1`: Always (Save also a single file which is not in the workspace folder)
- `2`: Workspace (Save only files within workspace folder)

Default: `1` (Always)

### g:local_history_path

Specify location for local history folder

Default: `.local-history`

### g:local_history_show_info_messages

Enable info message. If you find the vim-local-history message is annoying, then set it off. This configuration is used for development purposes.

Default: `v:false`

### g:local_history_max_changes

Maximum changes for each file. If the number of changes exceed `g:local_history_max_changes` the oldest change will be removed.

Default: `100`

### g:local_history_new_change_delay

A delay in seconds to create new change in local history (0: no delay). This configuration is used to avoid creating many changes in a short time. If saving time between 2 change is less than delay value, the content will be override for the lastest change instead of creating new change.

Default: `300` (5 minutes)

### g:local_history_width

Set the horizontal width of the local history graph (and preview).

Default: `45`

### g:local_history_preview_height

Set the vertical height of the local history preview.

Default: `15`

### g:local_history_exclude

Files or folders to not save.

```VimL
let g:local_history_exclude = [ '**/node_modules/**', '*.txt' ]
```

Default: `[]`

### g:local_history_mappings

Remap key bindings for local history functions

```VimL
let g:local_history_mappings = {
  \ "diff": ["d"],
  \ "quit": ["q", "Q"],
  \ "preview_bigger": ["b"],
  \ }
```

Please re-define all functions that is listed in the table above otherwise the non-mapping key are gone.

Default: See the table above

## Preview

Toggle local history

![](https://user-images.githubusercontent.com/17776979/91652188-d36c5700-eabe-11ea-93ab-1ea37be9aa5b.gif)

Delete local history change

![](https://user-images.githubusercontent.com/17776979/91652190-d8c9a180-eabe-11ea-89e8-e96e1463bd77.gif)

Revert local history change

![](https://user-images.githubusercontent.com/17776979/91652191-dbc49200-eabe-11ea-8285-b75fb17aa6fc.gif)

Show vertical diff

![](https://user-images.githubusercontent.com/17776979/91652193-de26ec00-eabe-11ea-8291-2fee515ed6a5.gif)

## Credits

- [Chadtree](https://github.com/ms-jpq/chadtree/) for setting up async python project.
- [vim-mundo](https://github.com/simnalamburt/vim-mundo) 
