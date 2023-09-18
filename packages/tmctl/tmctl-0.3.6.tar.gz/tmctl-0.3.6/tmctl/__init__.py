import fire

from .tmctl import TMCtl


def main():
    fire.Fire(TMCtl)
