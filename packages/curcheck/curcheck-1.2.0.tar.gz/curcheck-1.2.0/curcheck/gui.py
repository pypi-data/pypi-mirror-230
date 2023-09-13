import tkinter as tk
from tkinter import ttk
import asyncio


class Window():
    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry("1000x500")

        self._gui()

    def _gui(self):
        tk.Label(text="Роутеры: ").grid(column=3, row=3)
        tk.Label()


    async def show(self):
        while True:
            self.root.update()
            await asyncio.sleep(0.1)


async def main():
    window = Window()
    await window.show()

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
loop.run_until_complete(main())
