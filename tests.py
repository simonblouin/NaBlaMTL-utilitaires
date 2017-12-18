import NaBlaUtils as nbu
from glob import glob


if __name__ == '__main__':
    synths = glob('test/spectres/*')
    nbu.plot_spectre(synths, figname = 'spectres_tests.png')
    
    models = glob('test/models/*')
    # nbu.model_analysis(models)
    
    # print(synths)
    
