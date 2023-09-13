import PySimpleGUI as sg
from gpao_utils import interface_utils as iu

def frame_store(stores: list):
    layout_store = []
    for i, store in enumerate(stores):
        layout_store.append([   sg.Text(store.upper())   ])
        layout_store.append([   sg.Text(f" {i} - Chemin local vers le store", size=(iu.size_text, 1)), sg.InputText(sg.user_settings_get_entry(f"-MAP-STORE{i}-LOCAL", ""), key=f"-MAP-STORE{i}-LOCAL", size=(iu.size_text_big, 1)) ])
        layout_store.append([   sg.Text(f" {i} - store Windows (sur le noeud de calcul)", size=(iu.size_text, 1)), sg.InputText(sg.user_settings_get_entry(f"-MAP-STORE{i}-WIN", f"//store.ign.fr/{store}"), key=f"-MAP-STORE{i}-WIN", size=(iu.size_text_big, 1))])
        layout_store.append([   sg.Text(f" {i} - store Linux (sur le noeud de calcul)", size=(iu.size_text, 1)), sg.InputText(sg.user_settings_get_entry(f"-MAP-STORE{i}-UNIX", f"/var/data/{store}"), key=f"-MAP-STORE{i}-UNIX", size=(iu.size_text_big, 1)) ])
    return sg.Frame("", layout_store)
