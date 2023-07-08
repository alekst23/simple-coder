from human_eval.data import write_jsonl, read_problems
import os
import asyncio
from simple_coder import SimpleCoder

try:
    __IPYTHON__
    from tqdm.notebook import tqdm
except NameError:
    from tqdm import tqdm


C_OUTPUT_DIR = 'human-eval-output'


async def generate_one_completion(problems, task_id, n):
    print(f"generate_one_completion( {task_id} )")

    prompt = problems[task_id]["prompt"]

    working_dir = os.path.join(os.getcwd(), C_OUTPUT_DIR)
    tmp_file_name = f'{task_id}-{n}.py'.replace('/','-')
    tmp_file_path = os.path.join(working_dir, tmp_file_name)

    # pre-check
    if os.path.exists(tmp_file_path):
        file_size = os.path.getsize(tmp_file_path)
        if file_size > 0:
            with open(tmp_file_path, 'r') as f:
                return f.read()
    
    agenda = {
        'working_dir': working_dir,
        'requirements': f"Provide complete code for the following function signature: {prompt}",
        'output_file_name': tmp_file_name,
        'silent': False
    }
    
    coder = SimpleCoder(**agenda)
    await coder.run()
    
    with open(tmp_file_path, 'r') as f:
        output = f.read()
    
    return output


async def generate_one_completion_progress(pbar, **kwargs):
    res = await generate_one_completion(**kwargs)
    pbar.update(1)
    return res


async def generate_samples_taskid(pbar, problems, task_id, num_samples_per_task):
    tasks = [generate_one_completion_progress(pbar, problems=problems, task_id=task_id, n=i) for i in range(num_samples_per_task)]
    res = await asyncio.gather(*tasks)
    return res


async def generate_samples():
    problems = read_problems()
    task_ids = [x[1] for x in enumerate(problems.keys())]

    num_samples_per_task = 1
    total_samples = num_samples_per_task * len(task_ids)
    print(f"GENERATING {total_samples} SAMPLES")

    samples = []
    with tqdm(total=total_samples) as pbar:
        tasks = [generate_samples_taskid(pbar, problems, task_id, num_samples_per_task) for task_id in task_ids]
        results = await asyncio.gather(*tasks)
        
    for task_id, result in zip(task_ids, results):
        samples.extend([dict(task_id=task_id, completion=comp) for comp in result])        
    
    
    write_jsonl(os.path.join(os.getcwd(), C_OUTPUT_DIR, "samples.jsonl"), samples)


if __name__ == "__main__":
    asyncio.run(generate_samples())
