import glob, os,sys,imp,time


from itertools import product

from numba import cuda
import numpy as np

np.set_printoptions(threshold=sys.maxsize)
    
def __import__(module_name,class_name, globals=None, locals=None, fromlist=None):
    # Fast path: see if the module has already been imported.
    try:
        return sys.modules[module_name]
    except KeyError:
        pass

    # If any of the following calls raises an exception,
    # there's a problem we can't handle -- let the caller handle it.
    fp, pathname, description = imp.find_module(module_name)
    try:
        return imp.load_module(module_name, fp, pathname, description)    
    finally:
        # Since we may exit via an exception, close fp explicitly.
        if fp:
            fp.close()

def load_multiply(file,path):
    module_name = file.replace(path+"/", '')
    name_class = module_name.replace('.py', '')

    #print(file," :", name_class)
    name_import = file.replace('.py', '')
    module_name = __import__(name_import,name_class)

    variant_mul = getattr(module_name, name_class)

    mult_class = variant_mul()
    #print("max np:",np.max(mult_class.model)," min np:",np.min(mult_class.model))
    multiplier=cuda.to_device(np.array(mult_class.model,dtype=int))
    
    return multiplier,name_class

def __evaluate_multiply__(model,multiplier,images,labels):
    model.net.update_multipler([multiplier])
    Accuracy = model.evaluate(images,labels,False)

    return Accuracy


def evaluate_multiply_cominations(model,multiplier,images,labels,Accuracy_esatto=100.0,id_layer=-1):
    Accuracy = []
    Accuracy_loss = []
    Accuracy.append(Accuracy_esatto)
    Accuracy_loss.append(0.0)
    print('Layer appx:',model.net.get_Numbers_layer_with_multiply())
    print('Multiplier:',len(multiplier))
    print('Cominations:',len(multiplier)**model.net.N_layer_with_multiply)
    for id_multiplier in list(product(multiplier,repeat=model.net.N_layer_with_multiply)):
        comb_multiplier= multiplier[id_multiplier]
        Accuracy.append(__evaluate_multiply__(model,comb_multiplier,images,labels))
        Accuracy_loss.append(Accuracy[0]-Accuracy[-1])
        print( id_multiplier,': ',"{:>5}".format(round(Accuracy_loss[-1],2)),'\t(',"{:>5}".format(round(Accuracy[-1],2)),')%\t',round(model.elapsed_time,2),'s')

def evaluate_multiply(path,name,model,images,labels,Accuracy_esatto=100.0,id_layer=-1):


    save_file=model.save_csv_path+'Results_'+name+'.csv'
    #print(save_file)
    with open(save_file, 'w', encoding='UTF8', newline='') as f:
        print('Name, AccuracyLoss, Accuracy',file=f)
        f.close()

    variant_name = []
    Accuracy = []
    Accuracy_loss = []

    os.chdir(path)
    st = time.time()

    Accuracy.append(Accuracy_esatto)
    Accuracy_loss.append(0.0)
    variant_name.append('Esatto')
    files = sorted(glob.glob(path+"/*.py"))
    n_file = 0

    for file in files:

        multiplier,name_class = load_multiply(file,path)
        variant_name.append(name_class)

        #TODO: incapsulare bene
        model.net.update_multipler([multiplier])

        #Accuracy.append(model.evaluate(images,labels,False))
        Accuracy.append(__evaluate_multiply__(model,multiplier,images,labels))
        Accuracy_loss.append(Accuracy[0]-Accuracy[-1])
        

        print( name,' ',variant_name[-1],': ',"{:>5}".format(round(Accuracy_loss[-1],2)),'\t(',"{:>5}".format(round(Accuracy[-1],2)),')%\t',round(model.elapsed_time,2),'s')
        
        with open(save_file, 'a', encoding='UTF8', newline='') as f:
            print(name_class,str(Accuracy[-1]),str(Accuracy_loss[-1]),file=f, sep=',')
            f.close()

        n_file+=1

        #if n_file==5:
        #    break
        
        
    et = time.time()
    elapsed_time = et-st

    return n_file

def load_all_multiply(data_path):
    dirs = glob.glob(data_path+"*")
    multiplier = []
    for dir in dirs:
        if len(glob.glob(dir+"/*")) > 0:
            os.chdir(dir)
            files = sorted(glob.glob(dir+"/*.py"))
            
            for file in files:
                multiplier.append( load_multiply(file,dir),)
                return multiplier

def evaluete_all(data_path,model,images,labels,id_layer=-1):
    dirs = glob.glob(data_path+"*")
    n_dir = 0

    model.net.update_multipler([cuda.to_device(model.def_multiplier)])
    accuracy_esatto=model.evaluate(images,labels,True)
    print('Baseline Accuracy: \t\t\t(','{:>5}'.format(round(accuracy_esatto,2)),')%\t',round(model.elapsed_time,2),'s')
    #TODO: agiustare pachetti per usare il . format (chiedere a salvatore)

    total_file=0
    for dir in dirs:
        #print(dir)

        variant_type = dir.replace(data_path, '')
        if len(glob.glob(dir+"/*")) > 0:
            #print(dir)
            total_file+=evaluate_multiply(dir,variant_type,model,images,labels,accuracy_esatto,id_layer)
        
        n_dir+=1
        #if n_dir==2:
        #    break

    model.net.print_time_statics()
    print("Total Global time: ",model.total_elapsed_time," s")
    print('Total FPS:', total_file*len(images)/model.total_elapsed_time)
            


def evaluete_singol_layer_aproximate(data_path,model):
    for id_ciclo in range(len(model.net.layers)):
        if isinstance(model.net.layers[id_ciclo], (ConvLayer, DenseLayer)):
            
            for id_layer in range(len(model.net.layers)):

                if isinstance(model.net.layers[id_layer], (ConvLayer, DenseLayer)):
                    model.net.layers[id_layer].save_path_name=str('Apx_'+str(model.net.layers[id_ciclo].name)+'/')
                    #print(model.net.layers[id_layer].name)

            evaluete_all(data_path,model,id_ciclo)
    