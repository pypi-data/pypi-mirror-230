from torch.utils.data import Dataset,DataLoader
from transformers import AutoTokenizer,AutoConfig, AutoModel,DataCollatorForSeq2Seq
from torch.utils.data import Dataset,DataLoader
from typing import List, Optional, Tuple, Union


class Chatglm2_Dataset(Dataset):
    """
    import pandas as pd
    data =[{'prompt':"content",'response':"good"}]
    df_data = pd.DataFrame(data)
    """
    def __init__(self,df,
                 prompt_col = 'prompt',
                 response_col = 'response',
                 history_col = 'history',
                 max_context_length = 1024,
                 max_target_length = 1024,
                 trust_remote_code = True,
                 model_name_or_path= 'THUDM/chatglm2-6b'
                ):
        super(Chatglm2_Dataset).__init__()
        self.__dict__.update(locals())
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name_or_path, trust_remote_code=self.trust_remote_code) # cache_dir='./' Cache to the current working directory.
        
    def __len__(self):
        return len(self.df)
    
    def get(self,index):
        data = dict(self.df.iloc[index])
        example = {}
        example['context'] = self.tokenizer.build_prompt(query = data[self.prompt_col],history = data.get(self.history_col,None))
        example['target'] = data[self.response_col]
        return example 
    
    def __getitem__(self,index):
        example = self.get(index)
        a_ids = self.tokenizer.encode(text=example['context'], 
                add_special_tokens=True, truncation=True,
                max_length=self.max_context_length)
        b_ids = self.tokenizer.encode(text=example['target'], add_special_tokens=False, truncation=True,max_length=self.max_target_length)
        input_ids = a_ids + b_ids + [self.tokenizer.eos_token_id]
        labels = [-100]*len(a_ids)+b_ids+[self.tokenizer.eos_token_id]
        return {'input_ids':input_ids,'labels':labels}
    
def Llm_DataLoader(dataset,batch_size = 1,num_workers = 2, shuffle = True,model_name_or_path = 'THUDM/chatglm2-6b',trust_remote_code =True):
    """
     function is suitable for llm like ChatGPT and Baichuan.
    """
    tokenizer = AutoTokenizer.from_pretrained(model_name_or_path, trust_remote_code= trust_remote_code) # cache_dir='./' Cache to the current working directory.
    data_collator = DataCollatorForSeq2Seq(tokenizer,model=None,label_pad_token_id=-100,pad_to_multiple_of=None,padding=True)
    dl_train = DataLoader(dataset,batch_size = batch_size,num_workers = num_workers, shuffle = shuffle, collate_fn = data_collator)
    return dl_train

def build_chat_input(messages: List[dict], 
                      max_new_tokens = 2048,
                      model_max_length = 4096,
                      user_token_id = 195,
                      assistant_token_id = 196,
                      eos_token_id = 2,
                     trust_remote_code=True,
                     model_name_or_path= 'baichuan-inc/Baichuan2-13B-Chat'
                     ):
        tokenizer = AutoTokenizer.from_pretrained(model_name_or_path, use_fast=False, trust_remote_code=True)
        max_new_tokens = max_new_tokens
        max_input_tokens = model_max_length - max_new_tokens
        max_input_tokens = max(model_max_length // 2, max_input_tokens)
        total_input, round_input = [], []
        total_label, round_label =[],[]
        for i, message in enumerate(messages[::-1]):
            content_tokens = tokenizer.encode(message["content"])
            if message["role"] == "user":
                round_input = [user_token_id]+ content_tokens+ round_input
                round_label = [-100]+[-100 for _ in content_tokens]+ round_label
                if (total_input and len(total_input) + len(round_input) > max_input_tokens):
                    break
                else:
                    total_input = round_input + total_input
                    total_label = round_label + total_label
                    if len(total_input) >= max_input_tokens:
                        break
                    else:
                        round_input = []
                        round_label = []
            elif message["role"] == "assistant":
                round_input = [assistant_token_id]+ content_tokens+ [eos_token_id]+ round_input
                round_label = [-100]+ content_tokens+ [eos_token_id]+ round_label

            else:
                raise ValueError(f"message role not supported yet: {message['role']}")
        total_input = total_input[-max_input_tokens:]  # truncate left
        total_label = total_label[-max_input_tokens:]
        total_input.append(assistant_token_id)
        total_label.append(-100)
        return total_input,total_label
    
class Baichuan_Dataset(Dataset):
    """
    import pandas as pd
    data =[{'content':"good day",'response':"good"}]
    df_data = pd.DataFrame(data)
    """
    def __init__(self,df,
                ):
        self.df = df 
        
    def __len__(self):
        return len(self.df)
        
    def get_samples(self,index):
        samples = []
        d = dict(self.df.iloc[index])
        samples.append(d)
        return samples
    
    def get_messages(self,index):
        samples = self.get_samples(index)
        messages = []
        for i,d in enumerate(samples):
            if i==0:
                messages.append({'role':'user','content':d['content']}) ##  The prompt format is preprocessed before input.
            else:
                messages.append({'role':'user','content':d['content']})
            
            messages.append({'role':'assistant','content':d['response']})
        return messages
        
    def __getitem__(self,index):
        messages = self.get_messages(index)
        input_ids, labels = build_chat_input(messages)
        return {'input_ids':input_ids,'labels':labels}