#import "template/main.typ": example1

#let data = json(bytes(sys.inputs.data))
#example1(data.date)
