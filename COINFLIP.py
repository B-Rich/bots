
class CP_Exception (Exception) :
    def __init__(self,msg) :
        self.msg = msg

    def __str__(self) :
        return repr(self.msg)

class CP_Parser :

    special_characters = [';','(',')',',']
    arithOp = ['>','<','>=','<=','=']
    sensorTypes = ['WALL','BOT','ENEMY','FLOOR','FRIEND']
    moveDirection = ['FORWARD','BACKWARD','LEFT','RIGHT']
    turnDirection = ['LEFT','RIGHT']
    oneTokenAction = ['WAIT','SHOOT']


    @classmethod
    def tokenize(cls,code) :        
        code = code.upper()
        for sc in cls.special_characters + cls.arithOp :
            code = code.replace(sc,' {} '.format(sc))
        code = code.replace('\n',' ')
        return code.strip().split()
        

    @staticmethod
    def parse_code(code) :
        tokens = CP_Parser.tokenize(code)
        program = []
        i = 0
        j = 0
        while j < len(tokens) :
            if tokens[j] == ';' :
                program.append(CP_Parser.parse_decl(tokens[i:j]))
                i = j + 1
            j += 1

        return program
            
    @staticmethod
    def parse_decl(tokens) :
        if tokens[0] != 'IF' or not 'THEN' in tokens :
            raise CP_Exception("Incorrect declaration")
        then_pos = tokens.index('THEN')
        cond =  CP_Parser.parse_cond(tokens[1:then_pos])
        action = CP_Parser.parse_action(tokens[then_pos+1:])
        return cond,action
    
    @classmethod
    def parse_cond(cls,tokens) :
        if len(tokens) == 0 :
            raise CP_Exception("Incorrect condition")

        elif 'AND' in tokens or 'OR' in tokens :
            subcond = []
            lvl = 0
            res = ""
            for t in tokens :
                if lvl == 0 and (t == 'OR' or t == 'AND') :
                    if subcond[0] == '(' and subcond[-1] == ')' :
                        res += "( {} ) {} ".format(CP_Parser.parse_cond(subcond[1:-1]),t.lower())
                    else :
                        res += "{} {} ".format(CP_Parser.parse_cond(subcond),t.lower())
                    subcond = []
                else :
                    if t == '(' :
                        lvl += 1
                    elif t == ')' :
                        lvl -= 1
                    subcond.append(t)
            if subcond[0] == '(' and subcond[-1] == ')' :
                res += "({})".format(CP_Parser.parse_cond(subcond[1:-1]))
            else :
                res += CP_Parser.parse_cond(subcond)
            return res

        elif tokens[0] == 'NOT' :
            return "not {}".format(CP_Parser.parse_cond(tokens[1:]))
        elif tokens[0] == '(' and tokens[-1] == ')' :
            return "({})".format(CP_Parser.parse_cond(tokens[1:-1]))
        elif tokens == ['COINFLIP'] :
            return "self.coinflip"
        elif len(tokens) == 3 and tokens[0] == 'DICE' and tokens[1] in cls.arithOp :
            try :
                tokens[2] = str(int(tokens[3]))
            except ValueError :
                raise CP_Exception("Incorrect condition")
            return "self.dice {} {}".format(tokens[1],tokens[2])
        elif len(tokens) == 8 and tokens[0] == 'SENSOR' and tokens[1] == '(' and tokens[3] == ',' tokens[5] == ')' and tokens[6] == '=' and tokens[7] in cls.sensorTypes :
            try :
                x = str(int(tokens[2]))
                y = str(int(tokens[4]))
            except ValueError :
                raise CP_Exception("Incorrect condition")
            return "'{}' in self.sensor({},{})".format(tokens[7],x,y)
        else :
            raise CP_Exception("Incorrect condition")

    @classmethod
    def parse_action(cls,tokens) :
        if len(tokens) == 1 :
            t = tokens[0]
            if t in cls.oneTokenAction :
                return "self.action = '{}'".format(t)
            else :
                raise CP_Exception("Incorrect action")

        elif len(tokens) == 2 :
            t1,t2 = tokens
            if (t1 == 'MOVE' and t2 in cls.moveDirection]) or (t1 == 'TURN' and t2 in cls.turnDirection) :
                return "self.action = '{} {}'".format(t1,t2)
            else :
                raise CP_Exception("Incorrect action")
            
        else :
            raise CP_Exception("Incorrect action")



if __name__ == '__main__' :
    from sys import argv 
    with open(argv[1],'r') as f :
        program = f.read()
    print CP_Parser.parse_code(program)
