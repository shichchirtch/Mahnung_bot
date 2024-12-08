

class Mahnung:
    def __init__(self, titel:str|None, foto_id:str|None, za_chas:int|None, za_sutki, real_time:str, selector:str, job_id ):
        self.titel = titel
        self.foto_id = foto_id
        self.za_chas = za_chas
        self.za_sutki = za_sutki
        self.real_time = real_time
        self.selector = selector
        self.job_id = job_id
