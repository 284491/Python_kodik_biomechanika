import cv2
import numpy as np

# 1. Nový zoznam 20 bodov podľa tvojho zoznamu (obojstranne)
POINT_NAMES = [
    "Vrch hlavy",
    "Jugulum (krk)",

    # Pravá ruka
    "Pravé rameno", "Pravý lakeť", "Pravé zápästie", "Pravé končeky prstov",

    # Ľavá ruka
    "Ľavé rameno", "Ľavý lakeť", "Ľavé zápästie", "Ľavé končeky prstov",

    # Pravá noha
    "Pravá kyčel", "Pravé koleno", "Pravý členok", "Pravá päta", "Pravá špička",

    # Ľavá noha
    "Ľavá kyčel", "Ľavé koleno", "Ľavý členok", "Ľavá päta", "Ľavá špička"
]

clicked_points = []
img_original = None
img_display = None


def render_window():
    global img_display, img_original
    img_display = img_original.copy()

    # Horná tmavá lišta pre text
    cv2.rectangle(img_display, (0, 0), (img_display.shape[1], 45), (40, 40, 40), -1)

    idx = len(clicked_points)
    total = len(POINT_NAMES)

    if idx < total:
        instruction_text = f"[{idx + 1}/{total}] Klikni na: {POINT_NAMES[idx]}"
        color = (0, 255, 255)  # Žltá
    else:
        instruction_text = "Všetky body označené! Počítam ťažisko..."
        color = (0, 255, 0)  # Zelená

    cv2.putText(img_display, instruction_text, (15, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

    # Vykreslenie doteraz kliknutých bodov a ich čísel
    for i, (pt_x, pt_y) in enumerate(clicked_points):
        cv2.circle(img_display, (pt_x, pt_y), 4, (0, 255, 0), -1)
        cv2.putText(img_display, str(i + 1), (pt_x + 6, pt_y - 6),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 0), 1)


def click_event(event, x, y, flags, params):
    if event == cv2.EVENT_LBUTTONDOWN:
        if y < 45:  # Ignorovať kliknutia do lišty
            return

        if len(clicked_points) < len(POINT_NAMES):
            clicked_points.append((x, y))
            render_window()
            cv2.imshow("Vypocet taziska", img_display)


def render_window():
    global img_display, img_original
    img_display = img_original.copy()

    # Mierne zväčšíme výšku lišty (na 55px), aby sa tam vošli 2 riadky textu
    cv2.rectangle(img_display, (0, 0), (img_display.shape[1], 55), (40, 40, 40), -1)

    idx = len(clicked_points)
    total = len(POINT_NAMES)

    if idx < total:
        instruction_text = f"[{idx + 1}/{total}] Klikni na: {POINT_NAMES[idx]}"
        color = (0, 255, 255)  # Žltá
    else:
        instruction_text = "Všetky body označené! Počítam ťažisko..."
        color = (0, 255, 0)  # Zelená

    # Hlavný text inštrukcie
    cv2.putText(img_display, instruction_text, (15, 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.65, color, 2)

    # Nápoveda pre klávesové skratky
    controls_text = "Klávesy: [ Z ] = Krok späť  |  [ R ] = Reset  |  [ ESC ] = Koniec"
    cv2.putText(img_display, controls_text, (15, 47),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (180, 180, 180), 1)

    # Vykreslenie doteraz kliknutých bodov a ich čísel
    for i, (pt_x, pt_y) in enumerate(clicked_points):
        cv2.circle(img_display, (pt_x, pt_y), 4, (0, 255, 0), -1)
        cv2.putText(img_display, str(i + 1), (pt_x + 6, pt_y - 6),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 0), 1)
# Biomechanický model rozšírený o dlane a chodidlá
def calculate_center_of_mass(points):
    p = {i: np.array(pt) for i, pt in enumerate(points)}

    # Stred medzi pätou a špičkou pre chodidlá
    r_foot_center = (p[13] + p[14]) / 2
    l_foot_center = (p[18] + p[19]) / 2

    segments = [
        # Hlava a Trup
        {'p1': p[0], 'p2': p[1], 'weight': 0.074, 'ratio': 0.50},  # Hlava (Vrch hlavy -> Jugulum)
        {'p1': p[1], 'p2': (p[10] + p[15]) / 2, 'weight': 0.448, 'ratio': 0.42},  # Trup (Jugulum -> Stred kyčlí)

        # Pravá ruka
        {'p1': p[2], 'p2': p[3], 'weight': 0.029, 'ratio': 0.44},  # Rameno (Rameno -> Lakeť)
        {'p1': p[3], 'p2': p[4], 'weight': 0.017, 'ratio': 0.43},  # Predlaktie (Lakeť -> Zápästie)
        {'p1': p[4], 'p2': p[5], 'weight': 0.007, 'ratio': 0.39},  # Ruka (Zápästie -> Končeky prstov)

        # Ľavá ruka
        {'p1': p[6], 'p2': p[7], 'weight': 0.029, 'ratio': 0.44},  # Rameno
        {'p1': p[7], 'p2': p[8], 'weight': 0.017, 'ratio': 0.43},  # Predlaktie
        {'p1': p[8], 'p2': p[9], 'weight': 0.007, 'ratio': 0.39},  # Ruka

        # Pravá noha
        {'p1': p[10], 'p2': p[11], 'weight': 0.124, 'ratio': 0.43},  # Stehno (Kyčel -> Koleno)
        {'p1': p[11], 'p2': p[12], 'weight': 0.046, 'ratio': 0.41},  # Holeň (Koleno -> Členok)
        {'p1': p[12], 'p2': r_foot_center, 'weight': 0.016, 'ratio': 0.50},  # Chodidlo (Členok -> Stred chodidla)

        # Ľavá noha
        {'p1': p[15], 'p2': p[16], 'weight': 0.124, 'ratio': 0.43},  # Stehno
        {'p1': p[16], 'p2': p[17], 'weight': 0.046, 'ratio': 0.41},  # Holeň
        {'p1': p[17], 'p2': l_foot_center, 'weight': 0.016, 'ratio': 0.50},  # Chodidlo
    ]

    total_weight = sum(s['weight'] for s in segments)
    com = np.array([0.0, 0.0])

    for s in segments:
        seg_com = s['p1'] + s['ratio'] * (s['p2'] - s['p1'])
        com += seg_com * s['weight']

    com /= total_weight
    return (int(com[0]), int(com[1]))


def main(image_path):
    global img_original, img_display
    img_original = cv2.imread(image_path)

    if img_original is None:
        print("Chyba: Obrázok sa nepodarilo načítať.")
        return

    cv2.namedWindow("Vypocet taziska")
    cv2.setMouseCallback("Vypocet taziska", click_event)

    render_window()

    while True:
        cv2.imshow("Vypocet taziska", img_display)
        key = cv2.waitKey(100) & 0xFF
        if key in (ord('z'), ord('Z'), 8):
            if len(clicked_points) > 0:
                clicked_points.pop()  # Odstráni posledný pridaný bod
                render_window()
                print("-> Krok späť (posledný bod zmazaný)")

            # Reset všetkých bodov (kláves 'r' alebo 'R')
        elif key in (ord('r'), ord('R')):
            clicked_points.clear()  # Vymaže celý zoznam
            render_window()
            print("-> Resetované (všetky body zmazané)")

            # Koniec programu (ESC)
        elif key == 27:
            break

        # Po vykliknutí všetkých bodov
        if len(clicked_points) == len(POINT_NAMES):
            com_x, com_y = calculate_center_of_mass(clicked_points)

            # Vykreslenie ťažiska
            cv2.circle(img_display, (com_x, com_y), 9, (0, 0, 255), -1)
            cv2.circle(img_display, (com_x, com_y), 12, (0, 255, 255), 2)
            cv2.putText(img_display, "TAZISKO", (com_x + 15, com_y + 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            cv2.imshow("Vypocet taziska", img_display)
            print(f"\n=> Výsledné súradnice ťažiska: X={com_x}, Y={com_y}")
            cv2.waitKey(0)
            break

        if key == 27:  # ESC
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main("obrazok.jpg")