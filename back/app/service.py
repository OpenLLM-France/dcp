#!/usr/bin/env python3

import string
import random
import json
import hashlib

from sqlalchemy import exists, select, func, and_, distinct
from sqlalchemy.dialects.postgresql import insert as pg_insert

from models import normalize_json, User, UserSession, Task, UserTaskPermission, Prompt, Generation, GenerationView, GenerationParams, TaskInstance, Vote, Tag, Agreement, UserSignature, Bot, Instruction, Rating


class DataCollectionPlatform:

    def __init__(self):
        pass


    @classmethod
    def __generate_random_string(cls, length):
        characters = string.ascii_letters + string.digits
        return ''.join([random.choice(characters) for _ in range(length)])


    def add_task(self, db, name: str, public: bool, meta: str, instruction_id: int):
        db_task = Task(name=name, public=public, meta=meta, instruction_id=instruction_id)
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        return db_task.id


    def add_instruction(self, db, text):
        db_instruction = Instruction(text=text)
        db.add(db_instruction)
        db.commit()
        db.refresh(db_instruction)
        return db_instruction.id


    def add_prompt(self, db, task_id: int, text: str):
        db_prompt = Prompt(task_id = task_id, text=text)
        db.add(db_prompt)
        db.commit()
        db.refresh(db_prompt)
        return db_prompt.id


    def find_prompt(self, db, task_id: int, text: str):
        stmt = (
            select(Prompt)
               .where(
                    Prompt.task_id == task_id,
                    Prompt.text == text
               )
        )
        lst = db.execute(stmt).scalars().all()

        if 0 == len(lst):
            return None
        if len(lst) > 1:
            raise Exception(f'Too much ({len(lst)}) prompts for task_id=={task_id} and text=={text}.')

        return { 'id': lst[0].id, 'task_id': lst[0].task_id, 'text': lst[0].text }


    def add_usertaskpermission(self, db, user_id: int, task_id: int):
        db_usertaskpermission = UserTaskPermission(user_id=user_id, task_id=task_id)
        db.add(db_usertaskpermission)
        db.commit()


    def add_generation_params(self, db, params):
        d = None
        if isinstance(params, str):
            d = json.loads(params)
        else:
            d = params
        db_generation_params = GenerationParams(params=d)
        db.add(db_generation_params)
        db.commit()
        db.refresh(db_generation_params)
        return db_generation_params.id


    def add_generation(self, db, text, params_id, prompt_id):
        db_generation = Generation(text=text, params_id=params_id, prompt_id=prompt_id)
        db.add(db_generation)
        db.commit()
        db.refresh(db_generation)
        return db_generation.id


    def find_generation(self, db, text, params_id, prompt_id):
        stmt = (
            select(Generation)
               .where(
                    Generation.prompt_id == prompt_id,
                    Generation.params_id == params_id,
                    Generation.text == text
               )
        )
        lst = db.execute(stmt).scalars().all()

        if 0 == len(lst):
            return None
        if len(lst) > 1:
            raise Exception(f'Too much ({len(lst)}) generations for prompt_id=={prompt_id}, params_id=={params_id}and text=={text}.')

        return { 'id': lst[0].id, 'prompt_id': lst[0].prompt_id, 'params_id': lst[0].params_id, 'text': lst[0].text }


    def get_users(self, db):
        stmt = select(User)
        users = db.execute(stmt)
        lst = users.scalars().all()
        return lst


    def get_tasks(self, db):
        stmt = select(Task)
        tasks = db.execute(stmt)
        lst = tasks.scalars().all()
        return lst


    def get_prompts(self, db):
        stmt = select(Prompt)
        prompts = db.execute(stmt)
        lst = prompts.scalars().all()
        return lst


    def get_prompts_for_task(self, db, task_id):
        stmt = (
            select(Prompt)
               .where(Prompt.task_id == task_id)
               .order_by(Prompt.task_id)
        )
        result = db.execute(stmt)
        lst = [
            {
                'id': str(row.id),
                'text': row.text
            } for row, *_ in result
        ]
        return lst


    def get_generations(self, db):
        stmt = select(Generation)
        generations = db.execute(stmt)
        lst = generations.scalars().all()
        return lst


    def get_generations_for_prompt(self, db, prompt_id):
        stmt = (
            select(Generation)
               .where(Generation.prompt_id == prompt_id)
               .order_by(Generation.prompt_id)
        )
        result = db.execute(stmt)
        lst = [
            {
                'id': str(row.id),
                'params_id': str(row.params_id),
                'text': row.text
            } for row, *_ in result
        ]
        return lst


    def get_task_instances_for_prompt(self, db, prompt_id):
        stmt = (
            select(TaskInstance)
               .where(TaskInstance.prompt_id == prompt_id)
               .order_by(TaskInstance.prompt_id)
        )
        result = db.execute(stmt)
        lst = [
            {
                'id': str(row.id),
                'user_id': str(row.user_id),
                'generation_a_id': str(row.generation_a_id),
                'generation_b_id': str(row.generation_b_id),
                'timestamp': row.timestamp.timestamp()
            } for row, *_ in result
        ]
        return lst


    def get_votes_for_task_instance(self, db, task_instance_id):
        stmt = (
            select(Vote)
               .where(Vote.taskinstance_id == task_instance_id)
               .order_by(Vote.timestamp)
        )
        result = db.execute(stmt)
        lst = [
            {
                'id': str(row.id),
                'answer': row.answer,
                'timestamp': row.timestamp.timestamp()
            } for row, *_ in result
        ]
        return lst


    def get_tags_for_task_instance(self, db, task_instance_id):
        stmt = (
            select(Tag)
               .where(Tag.taskinstance_id == task_instance_id)
               .order_by(Tag.timestamp)
        )
        result = db.execute(stmt)
        lst = [
            {
                'id': str(row.id),
                'generation_id': str(row.generation_id),
                'label': row.label,
                'action': row.action_set,
                'timestamp': row.timestamp.timestamp()
            } for row, *_ in result
        ]
        return lst


    def find_generation_params(self, db, params):
        stmt = select(GenerationParams).where(
            GenerationParams.params == json.loads(normalize_json(params))
        )
        lst = db.execute(stmt).scalars().all()

        if 0 == len(lst):
            return None
        if len(lst) > 1:
            raise Exception(f'Too much ({len(lst)}) generation params for {params}.')

        return { 'id': lst[0].id, 'params': lst[0].params }


    def create_new_session_for_user(self, db, user_id):
        db_session = UserSession(user_id=user_id)
        db.add(db_session)
        db.commit()
        db.refresh(db_session)
        return db_session


    def add_user(self, db):
        db_user = User(login_name=self.__generate_random_string(16), login_name_in_use=False)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        db_session = self.create_new_session_for_user(db, db_user.id)

        return db_session.id, db_user.id


    def get_user_id(self, db, session_id):
        db_session = db.get(UserSession, session_id)
        if db_session is None:
            return None 
        return db_session.user_id


    def get_tasks_for_user(self, db, user_id):
        lst = []

        stmt_public = select(Task).where(Task.public == True)

        public_tasks = db.execute(stmt_public)

        for task in public_tasks.scalars().all():
            lst.append({ 'id': task.id, 'name': task.name })

        stmt_restricted = select(Task).where(
            exists().where(
                (UserTaskPermission.task_id == Task.id) &
                (UserTaskPermission.user_id == user_id)
            )
        )
        restricted_tasks = db.execute(stmt_restricted)

        for task in restricted_tasks.scalars().all():
            lst.append({ 'id': task.id, 'name': task.name })

        for task in lst:
            task['done'] = self.count_prompts_done_for_user_and_task(db, user_id, task['id'])
            task['total'] = self.count_prompts_for_task(db, task['id'])

        return lst


    def get_task_by_id(self, db, task_id):
        stmt = select(Task).where(Task.id == task_id)
        res = db.execute(stmt)
        db_task = res.scalars().one()
        return { 'id': db_task.id, 'name': db_task.name, 'meta': db_task.meta }


    def __get_least_touched_prompt(self, db, task_id, user_id):
        stmt = (
            select(
                Prompt,
                func.count(TaskInstance.id).label('task_instance_count')
            )
            .outerjoin(
                TaskInstance,
                (TaskInstance.prompt_id == Prompt.id) #& (TaskInstance.user_id == user_id)
            )
            .where(Prompt.task_id == task_id)
            .group_by(Prompt.id)
            .order_by(func.count(TaskInstance.id).asc())
            .limit(100)
        )

        res = db.execute(stmt).all()
        prompts = []

        min_cnt = None
        for prompt, cnt in res:
            if min_cnt is None:
                min_cnt = cnt
            elif min_cnt < cnt:
                break
            print(f'prompt {prompt.id} {cnt}')
            prompts.append(prompt)

        if 0 == len(prompts):
            raise 'No prompts for given task_id and user_id'

        random.shuffle(prompts)

        return prompts[0]


    def __get_least_viewed_generations(self, db, prompt_id, user_id):
        stmt = (
            select(
                Generation,
                func.count(GenerationView.id).label('generation_view_count')
            )
            .outerjoin(
                GenerationView,
                (Generation.id == GenerationView.generation_id) & 
                (GenerationView.user_id == user_id)  # Match both generation and user
            )
            .where(Generation.prompt_id == prompt_id)
            .group_by(Generation.id)
            .order_by(func.count(GenerationView.id).asc())
            .limit(100)
        )

        res = db.execute(stmt).all()
        generations = []

        min_cnt = None
        for gen, cnt in res:
            if min_cnt is None:
                min_cnt = cnt
            elif min_cnt < cnt and len(generations) >= 2:
                break
            print(f'gen    {gen.id} {cnt}')
            generations.append(gen)

        if len(generations) < 2:
            raise 'Not enougth generations for given prompt_id'

        random.shuffle(generations)

        return generations[:2]


    def __add_generation_view(self, db, user_id, generation_id):
        db_generation_view = GenerationView(user_id=user_id, generation_id=generation_id)
        db.add(db_generation_view)
        db.commit()
        db.refresh(db_generation_view)
        return db_generation_view.id


    def get_task_instance_for_user(self, db, task_id, user_id):
        db_prompt = self.__get_least_touched_prompt(db, task_id, user_id)
        generations = self.__get_least_viewed_generations(db, db_prompt.id, user_id)

        generation_a = generations[0]
        generation_b = generations[1]

        db_task_instance = TaskInstance(
            user_id=user_id,
            prompt_id=db_prompt.id,
            generation_a_id=generation_a.id,
            generation_b_id=generation_b.id
        )
        db.add(db_task_instance)
        db.commit()
        db.refresh(db_task_instance)

        # Update cache
        self.__add_generation_view(db, user_id, generation_a.id)
        self.__add_generation_view(db, user_id, generation_b.id)

        return {
            'id': db_task_instance.id,
            'prompt': db_prompt.text,
            'generations': [
                { 'id': generation_a.id, 'text': generation_a.text },
                { 'id': generation_b.id, 'text': generation_b.text }
            ]
        }


    def add_vote(self, db, task_instance_id, generation_a_id, generation_b_id, action, criterion, value):
        db_vote = Vote(
            taskinstance_id=task_instance_id,
            action_set=action,
            criterion=criterion,
            answer=value
        )
        db.add(db_vote)
        db.commit()
        db.refresh(db_vote)
        return db_vote


    def add_tag(self, db, task_instance_id, generation_id, action, tag):
        db_tag = Tag(
            taskinstance_id=task_instance_id,
            generation_id=generation_id,
            label=tag,
            action_set=action
        )
        db.add(db_tag)
        db.commit()
        db.refresh(db_tag)
        return db_tag


    def get_votes_since(self, db, timestamp, last_vote_id):
        stmt = (
            select(
                Vote.id,
                Vote.taskinstance_id,
                TaskInstance.user_id,
                TaskInstance.prompt_id,
                Vote.answer,
                Vote.timestamp
            )
            .join(TaskInstance, Vote.taskinstance_id == TaskInstance.id)
            .where(Vote.timestamp >= timestamp, Vote.id > last_vote_id)
        )
        
        result = db.execute(stmt)
        votes_with_info = [
            {
                "id": row.id,
                "taskinstance_id": row.taskinstance_id,
                "user_id": row.user_id,
                "prompt_id": row.prompt_id,
                "answer": row.answer,
                "timestamp": row.timestamp,
                "type": "vote"
            }
            for row in result
        ]
        return votes_with_info

    def get_tags_since(self, db, timestamp, last_tag_id):
        stmt = (
            select(
                Tag.id,
                Tag.taskinstance_id,
                TaskInstance.user_id,
                TaskInstance.prompt_id,
                Tag.generation_id,
                Tag.label,
                Tag.action_set,
                Tag.timestamp
            )
            .join(TaskInstance, Tag.taskinstance_id == TaskInstance.id)
            .where(Tag.timestamp >= timestamp, Tag.id > last_tag_id)
        )
        
        result = db.execute(stmt)
        tags_with_info = [
            {
                "id": row.id,
                "taskinstance_id": row.taskinstance_id,
                "user_id": row.user_id,
                "prompt_id": row.prompt_id,
                "generation_id": row.generation_id,
                "label": row.label,
                "set": row.action_set,
                "timestamp": row.timestamp,
                "type": "tag"
            }
            for row in result
        ]
        return tags_with_info


    def get_agreements_for_user(self, db, session_id):
        user_id = self.get_user_id(db, session_id)
        if not user_id:
            raise ValueError("Invalid session ID")

        stmt = (
            select(
                Agreement.id,
                Agreement.name,
                Agreement.description,
                UserSignature.timestamp)
            .outerjoin(
                UserSignature,
                and_(
                    Agreement.id == UserSignature.agreement_id,
                    UserSignature.user_id == user_id
                )
            )
            .order_by(Agreement.id)
        )

        # Execute the query
        result = db.execute(stmt).all()

        # Format the results
        lst = []
        for row in result:
            agreement_data = {
                "agreement_id": row.id,
                "agreement_name": row.name,
                "description": row.description,
                "signed_timestamp": row.timestamp.isoformat() if row.timestamp else None
            }
            lst.append(agreement_data)

        return lst


    def record_agreement(self, db, session_id, agreement_id):
        user_id = self.get_user_id(db, session_id)
        
        if not user_id:
            raise ValueError("Invalid session ID")
        
        # Check if already signed
        stmt = (
            select(UserSignature)
            .where(
                and_(
                    UserSignature.user_id == user_id,
                    UserSignature.agreement_id == agreement_id
                )
            )
        )
        
        existing = db.execute(stmt).first()
        if existing:
            return existing[0]  # Return the existing signature

        # Create a new signature
        db_signature = UserSignature(
            user_id=user_id,
            agreement_id=agreement_id
        )

        db.add(db_signature)
        db.commit()
        db.refresh(db_signature)
        return db_signature


    def get_agreement_text(self, db, agreement_id):
        stmt = (
            select(
                Agreement.name,
                Agreement.description,
                Agreement.text
            )
            .where(Agreement.id == agreement_id)
        )

        result = db.execute(stmt)

        for row in result:
            return { 'name': row.name, 'description': row.description, 'text': row.text }

        return None


    def add_agreement(self, db, name, description, text):
        db_agreement = Agreement(name=name, description=description, text=text)

        db.add(db_agreement)
        db.commit()
        db.refresh(db_agreement)

        return db_agreement


    def create_bot_session(self, db, model_name, prompt_template, config):
        stmt = (
            select(Bot)
            .where(
                Bot.model_name == model_name,
                Bot.prompt_template == prompt_template,
                Bot.config == config
            )
        )

        res = db.execute(stmt)
        bots_found = res.scalars().all()
        if len(bots_found) > 1:
            raise Exception(f'Too many bots found for "{model_name}", "{prompt_template}" and "{config}"')

        if 1 == len(bots_found):
            db_bot = bots_found[0]
            db_session = self.create_new_session_for_user(db, db_bot.user_id)
            session_id = db_session.id
            print(f'Bot found: user_id={db_bot.user_id} new session_id={session_id}')
            print(f'Config: {db_bot.config}')
        else:
            session_id, user_id = self.add_user(db)
            db_bot = Bot(user_id=user_id, model_name=model_name, prompt_template=prompt_template, config=config)
            db.add(db_bot)
            db.commit()
            db.refresh(db_bot)
            print(f'New bot created: user_id={user_id} new session_id={session_id} bot_id={db_bot.id}')

        return session_id


    def get_bot_info(self, db, user_id):
        stmt = (
            select(Bot)
            .where(Bot.user_id == user_id)
        )

        res = db.execute(stmt)
        bots_found = res.scalars().all()
        if len(bots_found) > 1:
            raise Exception(f'Too many bots found ({len(bots_found)}) for user_id=="{user_id}".')

        if 0 == len(bots_found):
            return None

        db_bot = bots_found[0]

        return {
            'model_name': db_bot.model_name,
            'prompt_template': db_bot.prompt_template,
            'config': db_bot.config
        }


    def get_stat_user_task(self, db):
        stmt = (
            select(
                TaskInstance.user_id,
                Prompt.task_id,
                func.count(TaskInstance.id).label("task_instance_count")
            )
            .join(Prompt, Prompt.id == TaskInstance.prompt_id)
            .group_by(TaskInstance.user_id, Prompt.task_id)
            .order_by(TaskInstance.user_id, Prompt.task_id)
        )

        results = db.execute(stmt).all()
        out = []
        for user_id, task_id, count in results:
            out.append({ 'user_id': user_id, 'task_id': task_id, 'count': count })

        return out


    def get_tasks_done_for_user(self, db, user_id):
        stmt = (
            select(
                Prompt.task_id,
                func.count(TaskInstance.id).label("task_instance_count")
            )
            .join(Prompt, Prompt.id == TaskInstance.prompt_id)
            .where(TaskInstance.user_id == user_id)
            .group_by(Prompt.task_id)
            .order_by(Prompt.task_id)
        )

        results = db.execute(stmt).all()
        out = []
        for task_id, count in results:
            out.append({ 'task_id': task_id, 'count': count })

        return out


    def get_tasks_done(self, db, task_id):
        stmt = (
            select(
                TaskInstance.user_id,
                func.count(TaskInstance.id).label("task_instance_count")
            )
            .join(Prompt, Prompt.id == TaskInstance.prompt_id)
            .where(Prompt.task_id == task_id)
            .group_by(TaskInstance.user_id)
            .order_by(TaskInstance.user_id)
        )

        results = db.execute(stmt).all()
        out = []
        for user_id, count in results:
            out.append({ 'user_id': user_id, 'count': count })

        return out


    def get_total_votes(self, db):
        stmt = select(func.count()).where(Vote.answer != -200)
        vote_count = db.scalar(stmt)

        return vote_count


    def get_tasks_done_for_user_and_task(self, db, user_id, task_id):
        stmt = (
            select(
                TaskInstance.user_id,
                Prompt.task_id,
                func.count(TaskInstance.id).label("task_instance_count")
            )
            .join(Prompt, Prompt.id == TaskInstance.prompt_id)
            .group_by(TaskInstance.user_id, Prompt.task_id)
            .where(user_id == TaskInstance.user_id, task_id == Prompt.task_id)
        )

        results = db.execute(stmt).all()
        out = []
        for user_id, task_id, count in results:
            out.append({ 'user_id': user_id, 'task_id': task_id, 'count': count })

        return out


    def count_prompts_for_task(self, db, task_id):
        stmt = (
            select(
                func.count(distinct(Prompt.id))
            )
            .where(Prompt.task_id == task_id)
        )

        results = db.execute(stmt).all()
        out = 0
        for count in results:
            out = count[0]

        return out


    def count_prompts_done_for_user_and_task(self, db, user_id, task_id):
        stmt = (
            select(
                func.count(distinct(Prompt.id))
            )
            .where(
                Prompt.task_id == task_id,
                exists().where(
                    TaskInstance.prompt_id == Prompt.id,
                    TaskInstance.user_id == user_id,
                    Vote.taskinstance_id == TaskInstance.id
                ).correlate(Prompt)
            )
        )

        results = db.execute(stmt).all()
        out = 0
        for count in results:
            out = count[0]

        return out


    def get_instruction_for_task(self, db, task_id):
        stmt = (
            select(Instruction)
            .join(Task, Task.instruction_id == Instruction.id)
            .where(Task.id == task_id)
        )

        result = db.scalars(stmt).first()
        return { 'id': result.id, 'text': result.text }


    def count_prompts_done_for_user(self, db, user_id):
        stmt = (
            select(
                func.count(distinct(Prompt.id))
            )
            .where(
                exists().where(
                    TaskInstance.prompt_id == Prompt.id,
                    TaskInstance.user_id == user_id,
                    Vote.taskinstance_id == TaskInstance.id
                ).correlate(Prompt)
            )
        )

        results = db.execute(stmt).all()
        out = 0
        for count in results:
            out = count[0]

        return out


    def get_rating(self, db, user_id, start = None, count = 10):
        stmt = (
            select(
                Rating.user_id,
                User.login_name,
                Bot.model_name,
                Rating.score
            )
            .join(User, Rating.user_id == User.id)
            .outerjoin(Bot, User.id == Bot.user_id)
            .order_by(Rating.score.asc())
        )

        results = db.execute(stmt).all()

        out = []
        num = 0
        current_user_pos, current_user_score = None, '⌛'
        for uid, login_name, model_name, score in results:
            if user_id == uid:
                id_to_display = 'moi'
                current_user_pos, current_user_score = num, score
            elif model_name is not None and len(model_name) > 0:
                id_to_display = '🤖 ' + model_name
            else:
                id_to_display = hashlib.sha512(login_name.encode('utf-8')).hexdigest()[:16]

            out.append({
                'num': num,
                'id': id_to_display,
                'user_id': uid,
                'score': score,
            })
            num += 1

        start_pos = 0
        if start is not None:
            start_pos = start
        elif current_user_pos is not None:
            start_pos = max(0, current_user_pos - int(count / 2))

        out = out[start_pos:start_pos+count]

        if current_user_pos is None:
            current_user_pos = '⌛'
        current_user_data = {
            'num': current_user_pos,
            'id': 'moi',
            'score': current_user_score,
            'count': self.count_prompts_done_for_user(db, user_id)
        }

        for item in out:
            item['count'] = self.count_prompts_done_for_user(db, item['user_id'])
            del item['user_id']

        return {
            'user': current_user_data,
            'list': out
        }


    def update_ratings(self, db, data: list[dict]):
        dialect = db.bind.dialect.name

        if dialect in ('postgresql'):
            stmt = pg_insert(Rating.__table__).values(data)
            stmt = stmt.on_conflict_do_update(
                index_elements = ['user_id'],
                set_ = { "score": stmt.excluded.score }
            )
        else:
            raise Exception('Only PostgreSql is supported now')
        db.execute(stmt)
        db.commit()


    # For update_rating.py script
    def get_all_votes(self, db):
        stmt = (
            select(
                Prompt.id.label("prompt_id"),
                TaskInstance.id.label("taskinstance_id"),
                TaskInstance.user_id,
                TaskInstance.generation_a_id,
                TaskInstance.generation_b_id,
                Vote.answer,
                Vote.timestamp
            )
            .select_from(Vote)
            .join(TaskInstance, Vote.taskinstance_id == TaskInstance.id)
            .join(Prompt, TaskInstance.prompt_id == Prompt.id)
            .order_by(Vote.timestamp.asc())
        )

        out = []
        for prompt_id, taskinstance_id, user_id, generation_a_id, generation_b_id, answer, timestamp in db.execute(stmt).all():
            out.append({
                'user_id': user_id,
                'prompt_id': str(prompt_id),
                'taskinstance_id': str(taskinstance_id),
                'generation_a_id': str(generation_a_id),
                'generation_b_id': str(generation_b_id),
                'answer': answer,
                'timestamp': timestamp.timestamp()
            })

        return out


    def get_user_bot(self, db):
        stmt = (
            select(User.id.label('user_id'), Bot.model_name)
            .join(Bot, User.id == Bot.user_id, isouter=True)
            .order_by(User.id.asc())
        )

        out = []

        for user_id, model_name in db.execute(stmt).all():
            out.append({
                'user_id': user_id,
                'model_name': model_name
            })

        return out
