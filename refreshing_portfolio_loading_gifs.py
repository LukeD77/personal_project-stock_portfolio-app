### File that runs a loading popup until the finished_flag file is written to say finished. It then rewrites the flag to say idle.

import numpy as np
import pickle
import PySimpleGUI as sg
import os

def loading_gif():
    gif_list = os.listdir('gifs')
    n = np.random.randint(0,len(gif_list))
    gif = str('./gifs/' + gif_list[n])

    with open('finished_flag.p', 'wb') as f:
        pickle.dump('Running',f)
    end_value = 'Running'
    i=0
    while True:
        loading_popup = sg.PopupAnimated(gif,message='Refreshing portfolio page...',
                                         font='Helvitica 22 bold',text_color='black',
                                         keep_on_top=True, time_between_frames=65,
                                         background_color='white')
        i+=1
        if i%100 == 0:
            with open('finished_flag.p', 'rb') as f:
                end_value = pickle.load(f)
        if end_value == 'Finished':
            with open('finished_flag.p', 'wb') as f:
                pickle.dump('Idle',f)
            sg.PopupAnimated(None)
            sg.PopupAutoClose('Portfolio has been updated!', auto_close_duration=3,
                              font = 'Helvitica 22 bold', text_color='white',
                              background_color='black',keep_on_top=True,no_titlebar=True,
                             button_type=5)
            break

def main():
    loading_gif()


if __name__ == '__main__':
    main()
