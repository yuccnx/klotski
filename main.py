#-*- coding: UTF-8 -*-

import json

import model
import view

def main():

    conf_file = open("./conf/conf.json")
    conf = json.loads(conf_file.read())

    state_file = open("./conf/state.json")
    state = json.loads(state_file.read())

    g = model.Game()
    print("thinking...")
    boards = g.play(state)
    if len(boards) == 0:
        print("not found result~")
        return

    # display = view.TextDisplayer()
    display = view.ImageDisplayer(conf["display"])
    display.displays(boards)


if __name__ == '__main__':
    main()



