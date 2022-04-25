import threading, gui, computing, data_base


if __name__ == "__main__":
    data = data_base.Application()
    window = gui.Window(data)
    calcul = computing.Shelling_calculating(data, window)
    status = threading.Thread(target=calcul.start_calc)
    status.start()
    window.mainloop()
