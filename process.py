import ctypes
from ctypes import*
import sys

max_deskew_attempts = 5
mydll = windll.LoadLibrary("C:\\Projects\\Claims\\ISP2003.dll")
dll96v1 = windll.LoadLibrary("C:\\Projects\\Claims\\CRDE2003.dll")

def rotate(mem):
    mydll.tdeskew.restype = ctypes.c_double
    for x in range(0, max_deskew_attempts):
        result = mydll.tdeskew(mem,
                                 ctypes.c_short(1),     #Subsampling
                                 ctypes.c_double(90),   #Range
                                 ctypes.c_double(0.1),  #DeskewAngle_res
                                 ctypes.c_double(4.0),  #line resolution
                                 c_byte(0))             #DeskewGrayValue
        print 'tdeskew: %s' % result

        class RECT(Structure):
            _fields_ = [("x", c_int),
                        ("y", c_int),
                        ("w", c_int),
                        ("h", c_int)]
        rect = RECT(0,0,2550,3300) #Need to read this dynamically

        result = -result #rotate in other direction to current skew
        #if result > 0:
            #result = - (360 - result)
        mem = mydll.ILRotate(mem,
                                ctypes.c_double(result),
                                byref(rect),
                                0xFFFFFF)
        #We then need to resize (CopyCropDib) as this will have grown or shrunk the image size
        print 'ILRotate: %s' % result
    return mem

def processpage(pagenum, append):
    print 'Page: %s' % pagenum
    mem = POINTER(c_ubyte)()
    #How do we free "mem" after?
    result = dll96v1.readtiffiledib("C:\\Projects\\Claims\\Claims_Batch.tif",
                                    1,
                                    0,
                                    pagenum, #Page
                                    byref(mem),
                                    0,
                                    0,
                                    0,
                                    "unilzw")
    #print result, sys.getsizeof(mem)
    print result

    #mem = rotate(mem)

    mem = mydll.CropAutoDib(mem,
                            40, #Sensitivity 1 to 255
                            0, 0)
    mem = rotate(mem)
    mem = mydll.CropAutoDib(mem,
                            10, #Sensitivity 1 to 255
                            0, 0)

    result = dll96v1.writetiffiledib("C:\\Projects\\Claims\\Claims_Batch_1.tif",
                                     4,
                                     1,
                                     append, #append, 1 for yes, 0 for no
                                     mem,
                                     0,
                                     0,
                                     0,
                                    "unilzw")
                                     

    #print result


p = create_string_buffer("boxmsg")
result = mydll.DllInit(-1,
                       #('\0'.join("boxmsg"))) #'\0'.join(
                       byref(p))

#processpage(3, 0)
for x in range(0, 52):
    processpage(x, 1)


"""

# Load DLL into memory.
hllDll = ctypes.WinDLL ("C:\\Projects\\Claims\\ISP2003.dll")

# Set up prototype and parameters for the desired function call.
# HLLAPI

hllApiProto = ctypes.WINFUNCTYPE (ctypes.c_int,
                                  ctypes.c_long,
                                  ctypes.c_long,
                                  ctypes.c_void_p,  #Call back, I assume this is the data type
                                  ctypes.c_int)
hllApiParams = (1, "p1", 0), (1, "p2", 0), (1, "p3",0), (1, "p4",0),

# Actually map the call ("HLLAPI(...)") to a Python name.

hllApi = hllApiProto (("CropAutoDib", hllDll), hllApiParams)

# This is how you can actually call the DLL function.
# Set up the variables and call the Python name with them.

p1 = ctypes.c_int (1)
p2 = ctypes.c_long(0)
p3 = ctypes.c_long(1)
p4 = ctypes.c_void_p (0)
hllApi (ctypes.byref (p1),ctypes.byref( p2), ctypes.byref (p3), ctypes.byref (p4))

"""
