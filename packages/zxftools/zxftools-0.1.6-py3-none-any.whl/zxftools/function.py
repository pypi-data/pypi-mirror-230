from transformers_stream_generator import init_stream_support
import torch
def make_prompt(query,history):
    return f"""The following is a conversation between a human and an AI assistant namely YuLan, 
This is chat history:
{history}
[|Human|]:{query}\n[|AI|]:"""
# 用户Triton 的自定义函数
def stream_generator(model,tokenizer,query,history=[],
                    top_k=20,top_p=0.95,max_length=2000,
                                           temperature=0.8,device=0):
    init_stream_support()
    prompt = make_prompt(query,history)
    input_ids = tokenizer(
            prompt, return_tensors="pt", add_special_tokens=False,
        ).input_ids.cuda(device)

    with torch.no_grad():
        generator = model.generate(
            input_ids,
            # seed=0,
            do_sample=True,
            do_stream=True,
            # top_k=top_k,
            # top_p=top_p,
            max_length=max_length,
            # temperature=temperature,
        )
        stream_result = ""
        words = ""
        last_tokens = []
        last_decoded_tokens = []

        for index, x in enumerate(generator):
            tokens = x.cpu().numpy().tolist()
            tokens = last_tokens + tokens
            word = tokenizer.decode(tokens, skip_special_tokens=True)
            if "�" in word:
                last_tokens = tokens
            else:
                if " " in tokenizer.decode(
                    last_decoded_tokens + tokens, skip_special_tokens=True
                ):
                    word = " " + word
                last_tokens = []
                last_decoded_tokens = tokens

            if "�" not in word:
                stream_result += word
                if history == []:
                    yield (stream_result,[(query,stream_result)])
                else:
                    yield (stream_result,history+[(query,stream_result)])

# English plan generator
def run(test_list: list, day: int, show=True):
    day_study = []
    day_reset = []
    day_plan = []
    assert len(test_list) == 21

    def review_(day: int):
        if i >= day:
            try:
                day_reset.append(test_list[i - day])
            except:
                pass

    for i in range(43):
        try:
            day_study.append(test_list[i])
            day_reset.append(test_list[i])
        except:
            pass
        review_(1);
        review_(3);
        review_(8);
        review_(15);
        review_(30)
        day_plan.append([day_study, day_reset])
        day_study, day_reset = [], []
    plan = day_plan[day - 1]
    return f"study:{plan[0]}- review{plan[1]}" if show else plan
