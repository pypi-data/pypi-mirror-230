class EmailValidator:

    def is_valid(self, email) -> bool:
        cnt = 0
        idx = -1
        for i in range(len(email)):
            if(email[i] != '@'): continue
            idx = i
            cnt += 1
        if(cnt != 1 or idx == 0 or idx == len(email) - 1): return False
        return True