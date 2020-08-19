import pynvim

@pynvim.plugin
class LocalHistoryPlugin(object):
    def __init__(self, nvim: pynvim.Nvim):
        self.nvim = nvim

    @pynvim.autocmd('BufWritePost', pattern = '*', eval = 'expand(\'%:p\')', sync = True)
    def on_buffer_write_post(self, file_name):
        self.nvim.out_write('Test plugin ' + file_name + '\n')

