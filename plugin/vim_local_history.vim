if exists('s:vim_local_history_loaded')
  finish
endif

let s:vim_local_history_loaded = 1

if !exists('g:local_history_path')
  let g:local_history_path = '.local_history'
endif

if !exists('g:local_history_max_display')
  let g:local_history_max_display = 50
endif

if !exists('g:local_history_save_delay')
  let g:local_history_save_delay = 300
endif
