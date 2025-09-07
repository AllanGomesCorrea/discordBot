from .summary import summary
from .total_splited import total_splited
from .hello import hello
from .play_song import add_song, play_pause, skip, queue, exit
from .save_monthly import save_monthly
from .load_monthly import load_monthly

def register_commands(bot):
    bot.tree.add_command(summary)
    bot.tree.add_command(total_splited)
    bot.tree.add_command(hello)
    bot.tree.add_command(add_song)
    bot.tree.add_command(play_pause)
    bot.tree.add_command(skip)
    bot.tree.add_command(queue)
    bot.tree.add_command(exit)
    bot.tree.add_command(save_monthly)
    bot.tree.add_command(load_monthly)
