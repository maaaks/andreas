from typing import List, Tuple

from andreas.functions.process_event import process_event
from andreas.functions.querying import get_comments_list
from andreas.functions.verifying import sign_post
from andreas.models.event import Event
from andreas.models.post import Post
from andreas.models.relations import UserPostRelation
from andreas.models.user import User
from andreas.tests.andreastestcase import AndreasTestCaseWithKeyPair


class TestCommenting(AndreasTestCaseWithKeyPair):
    def setUpSafe(self):
        super().setUpSafe()
        
        self.post = Post()
        self.post.server = self.server
        self.post.path = 'post1'
        self.post.data = {
            'body': 'How are you?',
        }
        self.post.save()
        UserPostRelation.create(source=self.abraham, type='wrote', target=self.post)
        
        self.comments_data: Tuple[Tuple[ List[int], User, str ]] = (
            ([1], self.bernard, 'Good!'),
            ([1, 3], self.abraham, 'Bernard, what are you doing here?'),
            ([1, 3, 5], self.bernard, 'Imitating a conversation with you!'),
            ([1, 3, 5, 6], self.abraham, 'Thank you! This means a lot to me.'),
            ([1, 3, 5, 6, 7], self.bernard, ';-)'),
            ([2], self.bernard, 'By the way, happy birthday, Abraham!'),
            ([2, 4], self.abraham, 'Thank you!!!'),
        )
        
        for breadcrumbs, author, body in self.comments_data:
            event = Event()
            if len(breadcrumbs) == 1:
                event.parent = 'aaa/post1'
            else:
                event.parent = f'aaa/post1#c{breadcrumbs[-2]}'
            event.server = 'aaa'
            event.path = f'post1#c{breadcrumbs[-1]}'
            event.diff = { 'body': body }
            event.authors = [repr(author)]
            event.signatures = { repr(author): sign_post(event, self.keypairs[author]).hex() }
            event.save()
            process_event(event)
    
    def test_get_comments_list(self):
        expected = []
        for (breadcrumbs, author, body) in self.comments_data:
            expected.append((len(breadcrumbs), repr(author), body))
        
        results = []
        for level, comment in get_comments_list(self.post):
            results.append((level, repr(comment.authors()[0]), comment.data['body']))
        
        self.assertEqual(expected, results)