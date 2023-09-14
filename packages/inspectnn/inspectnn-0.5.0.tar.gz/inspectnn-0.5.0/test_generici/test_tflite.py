import tflite


def LayerOpcodeConverter(id):
    return model.OperatorCodes(id).BuiltinCode()


f = open("/home/filippo/Git/PhD_AdversarialAttack/Models/ResNet8-quantized.tflite","rb")
buf = f.read()

model = tflite.Model.GetRootAsModel(buf,0)

print("len:",model.SubgraphsLength())
graf = model.Subgraphs(0)

for i in range(graf.OperatorsLength()):
    op=graf.Operators(i)
    
    print(i,tflite.utils.BUILTIN_OPCODE2NAME[LayerOpcodeConverter(op.OpcodeIndex())],op.InputsLength(),op.OutputsLength())
    
    for j in range(op.InputsLength()):
        print("\t",op.Inputs(j))

    print("OUT:",op.Outputs(0))
    
print("# TEST PASS")