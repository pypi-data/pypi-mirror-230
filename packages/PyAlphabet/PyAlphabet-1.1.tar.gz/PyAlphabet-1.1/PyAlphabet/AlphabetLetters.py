class AlphabetLetters:
    def __init__(self, start_letter: str, end_letter: str, flag_line=False, flag_upper=True, flag_lower=True, flag_reflected=False) -> None:
        self.pos_start_letter = start_letter
        self.pos_end_letter = end_letter
        self.to_line = flag_line
        self.to_upper = flag_upper
        self.to_lower = flag_lower
        self.to_reflected = flag_reflected

    def alphabet(self) -> str:        
        alphabet_text = ""


        if self.to_upper == False \
            and self.to_lower == False:
            return None

        for i in range(ord(self.pos_start_letter.lower()), ord(self.pos_end_letter.lower())+1):
            if self.to_upper:
                alphabet_text += chr(i).upper()
            
            if self.to_lower:
                alphabet_text += chr(i) + " "
            
            if self.to_line:
                alphabet_text += "\n"
 
        if self.to_reflected:
            return alphabet_text[::-1]

        return alphabet_text