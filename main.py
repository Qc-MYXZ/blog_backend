from apps.run import create_app_test
print("11111")
app = create_app_test()
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8888,
        reload=False,
    )
