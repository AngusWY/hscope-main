
import util

AnalyzerInternal = util.SimpleEnum({
    "TRUE"                          : "true",
    "FALSE"                         : "false",
    "NULL"                          : "null",
    "UNDEFINED"                     : "undefined",
    "HOLE"                          : "hole",   
    # Constants
    "THIS"                          : "%this",
    "ANONYMOUS"                     : "%mm",
})