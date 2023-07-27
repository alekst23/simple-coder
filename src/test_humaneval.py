import asyncio
from human_eval.data import write_jsonl, read_problems
import os
from simple_coder import SimpleCoder
import logging

try:
    __IPYTHON__
    from tqdm.notebook import tqdm
except NameError:
    from tqdm import tqdm

logger = logging.getLogger(__name__)


def get_file_path(task_id, output_dir):
    working_dir = os.path.join(os.getcwd(), output_dir)
    tmp_file_name = f'{task_id}.py'.replace('/', '-')
    return os.path.join(working_dir, tmp_file_name)


async def generate_one_completion(problems, task_id, output_dir):
    logger.info(f"generate_one_completion( {task_id} )")

    prompt = problems[task_id]["prompt"]
    tmp_file_path = get_file_path(task_id, output_dir)

    # pre-check
    if os.path.exists(tmp_file_path):
        file_size = os.path.getsize(tmp_file_path)
        if file_size > 0:
            try:
                with open(tmp_file_path, 'r') as f:
                    return f.read()
            except IOError:
                logger.error(f"Error reading file: {tmp_file_path}")

    agenda = {
        'working_dir': output_dir,
        'requirements': f"Provide complete code for the following function signature: {prompt}",
        'output_file_name': tmp_file_path,
        'silent': False
    }

    # Create the agent with an agenda for this sample
    coder = SimpleCoder(**agenda)

    # Run the coder
    await coder.run()

    # Read the output file
    try:
        with open(tmp_file_path, 'r') as f:
            output = f.read()
    except IOError:
        logger.error(f"Error reading file: {tmp_file_path}")

    return output


async def generate_samples(output_dir):
    problems = read_problems()
    task_ids = [x[1] for x in enumerate(problems.keys())]

    total_samples = len(task_ids)
    logger.info(f"GENERATING {total_samples} SAMPLES")

    samples = []
    with tqdm(total=total_samples) as pbar:
        for task_id in task_ids:
            result = await generate_one_completion(problems, task_id, output_dir)
            samples.append(dict(task_id=task_id, completion=result))
            pbar.update(1)

    write_jsonl(os.path.join(os.getcwd(), output_dir, "samples.jsonl"), samples)


if __name__ == "__main__":
    output_dir = 'test-output/human-eval-output-3.5'
    asyncio.run(generate_samples(output_dir))
