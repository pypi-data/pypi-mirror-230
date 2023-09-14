import time
import tqdm

def main():
    steps = ['Opening Visual Studio',
             'Creating New Project',
             'Windows Form',
             'A-P-P',
             'Waking up Online Students']
    pbar = tqdm.tqdm(steps, leave=False)
    for step in pbar:
        pbar.set_description(f'{step}')
        time.sleep(1)

main()