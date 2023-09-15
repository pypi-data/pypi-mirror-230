from datetime import datetime


class Schedule:

    def __init__(self, schedule_id, command, date_to_execute, status, modo_integracao):
        self.schedule_id = schedule_id
        self.command = command
        self.date_to_execute = date_to_execute
        self.date_executed = None
        self.status = status
        self.finished = False
        self.modo_integracao = modo_integracao

    def executing(self):
        self.status = 'EXECUTING'

    def executed(self):
        self.date_executed = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.status = 'EXECUTED'
        self.finished = True

    def failed(self):
        self.status = 'FAILED'

    def canceled(self):
        self.status = 'CANCELED'

    def to_json(self):
        return {
            'schedule_id': self.schedule_id,
            'command': self.command,
            'date_to_execute': self.date_to_execute,
            'date_executed': self.date_executed,
            'status': self.status,
            'finished': self.finished,
            'modo_integracao': self.modo_integracao
        }
