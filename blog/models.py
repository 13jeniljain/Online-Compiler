# Create your models here.

from django.db import models

class Problem(models.Model):
    prob_id = models.AutoField(primary_key=True)
    prob_title = models.CharField(max_length=50)
    prob_desc = models.TextField()
    prob_diff = models.CharField(max_length=10)

class TestCase(models.Model):
    test_id = models.AutoField(primary_key=True)
    prob_id = models.ForeignKey(Problem, on_delete=models.CASCADE)
    test_in = models.TextField(default = 1)
    test_out = models.TextField(default = 1)


class Submission(models.Model):
    sub_id = models.AutoField(primary_key=True)
    prob_id = models.ForeignKey(Problem, on_delete=models.CASCADE)
    verdict = models.CharField(max_length=5)
    u_id = models.ForeignKey('auth.user', on_delete=models.CASCADE)

    
