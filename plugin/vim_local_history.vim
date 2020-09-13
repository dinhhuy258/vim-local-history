if exists('s:vim_local_history_loaded')
   finish
endif

let s:vim_local_history_loaded = 1

let g:local_history_workspace = getcwd()

if get(g:, 'huy_duong_workspace', 0) == 1
  nnoremap <silent> <F5> :LocalHistoryToggle<CR>

  let g:local_history_path = '/Users/dinhhuy258/.local-history'
  let g:local_history_enabled = 2
endif

