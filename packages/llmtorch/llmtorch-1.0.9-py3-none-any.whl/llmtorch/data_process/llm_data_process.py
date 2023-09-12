from torch.utils.data import Dataset,DataLoader
from transformers import AutoTokenizer,AutoConfig, AutoModel,DataCollatorForSeq2Seq
from torch.utils.data import Dataset,DataLoader 
class Chatglm2_Dataset(Dataset):
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
    
def Chatglm2_DataLoader(dataset,batch_size = 1,num_workers = 2, shuffle = True,model_name_or_path = 'THUDM/chatglm2-6b',trust_remote_code =True):
    tokenizer = AutoTokenizer.from_pretrained(model_name_or_path, trust_remote_code= trust_remote_code) # cache_dir='./' Cache to the current working directory.
    data_collator = DataCollatorForSeq2Seq(tokenizer,model=None,label_pad_token_id=-100,pad_to_multiple_of=None,padding=True)
    dl_train = DataLoader(dataset,batch_size = batch_size,num_workers = num_workers, shuffle = shuffle, collate_fn = data_collator)
    return dl_train