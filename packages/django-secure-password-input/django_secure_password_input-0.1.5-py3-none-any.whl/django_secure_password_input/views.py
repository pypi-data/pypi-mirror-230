from django.shortcuts import render
from django.http import JsonResponse
from .settings import public_key_text
from .settings import public_key

def getPublicKey(request):
    return JsonResponse({
        "success": True,
        "result": {
            "publicKey": public_key_text,
            "e": str(public_key.e),
            "n": str(public_key.n),
        }
    })
