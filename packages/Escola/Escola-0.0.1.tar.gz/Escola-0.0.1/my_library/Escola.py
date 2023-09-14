class Pessoa():
    
    def __init__(self, nome, CPF, telefone, email):
        
        self.nome = nome
        self.CPF = CPF
        self.telefone = telefone
        self.email = email
        
        
    def cadastar(self):
        
        print("Cadastro feito com sucesso!\n" + "Nome: " + str(self.nome) + 
              "\n" + "CPF: " + str(self.CPF) + "\n" + "Telefone: " + 
              str(self.telefone) + "\n" + "Email: " + str(self.email) + "\n")
        
class Coordenador(Pessoa):
    
    def __init__(self, nome, CPF, telefone, email, setor):
        
        super().__init__(nome, CPF, telefone, email)        
        self.setor = setor
        
    def visualizar_setor(self):
        
        print("Esse(a) coordenador(a) é responsável pelo setor " + 
              str(self.setor)  +"." + "\n")
        
class Professor(Pessoa):
    
    def __init__(self, nome, CPF, telefone, email, materia, turma):
        
        super().__init__(nome, CPF, telefone, email)
        self.materia = materia
        self.turma = turma
        
    def visualizar_turma_materia(self):
        
        print("Esse(a) professor(a) é responsável pela turma " + 
              str(self.turma) + "." + "\n")
        
    def toString(self):
         
        return f'{self.nome} {self.materia} {self.turma}'
        
class Aluno(Pessoa):
    
    def __init__(self, nome, CPF, telefone, email, serie, matricula, nota1, 
                 nota2, nota3, qtd_advertencias, turma):
        
        super().__init__(nome, CPF, telefone, email)
        self.serie = serie
        self.matricula = matricula
        self.nota1 = nota1
        self.nota2 = nota2
        self.nota3 = nota3
        self.qtd_advertencias = qtd_advertencias
        self.turma = turma
        
    def calcular_media_final(self):
        
        self.media = (((self.nota1 + self.nota2 + self.nota3)/3) - 
                 0.1*self.qtd_advertencias)
        
        print("Sua média final é " + str(self.media) + ".\n")
        
    def visualizar_status(self):
        
        if(self.media >= 5):
            print("Este aluno(a) está aprovado! Parabéns!\n")
            
        else:
            print("O aluno está reprovado.")
            
class Turma():
    
    def __init__(self, cod, materia, qtd_vagas, qtd_alunos, dia_semana, horario, 
                 duracao_curso):
        self.cod = cod
        self.materia = materia
        self.qtd_vagas = qtd_vagas
        self.qtd_alunos = qtd_alunos
        self.dia_semana = dia_semana
        self.horario = horario
        self.duracao_curso = duracao_curso
        
    def atualizar_qtd_alunos(self, nova_qtd):
        self.qtd_alunos = nova_qtd
        
        salva = self.qtd_vagas - self.qtd_alunos
        
        print("Esta turma possui " + str(self.qtd_alunos) + 
              " alunos atualmente. Restam " + str(salva) + " vagas!\n")
        
    def visualizar_info(self):
        
        print("Turma: " + str(self.cod) + "\n" + "Matéria: " + 
              str(self.materia) + "\n" + "Dia da semana: " + 
              str(self.dia_semana) + "-feira \n" + "Horário: " + 
              str(self.horario) + "\n" "Duração: " + str(self.duracao_curso) + 
              " meses \n" + "Vagas: " + str(self.qtd_vagas) + "\n" + 
              "Vagas preenchidas: " + str(self.qtd_alunos) + "\n")
        
    def toString(self):
        
        return f'{self.cod} {self.dia_semana} {self.horario}'
        

            
        
        
        
    
    
        
    
    
    

