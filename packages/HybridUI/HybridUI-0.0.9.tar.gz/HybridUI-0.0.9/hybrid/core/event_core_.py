import asyncio
from dataclasses import dataclass, field
from queue import Queue
from threading import Event
from typing import Callable, List
import socketio
 
@dataclass
class EventListener:
    classes: dict = field(default_factory=dict)
    functions: dict = field(default_factory=dict)
    socket_manager: Callable= None
 
    def register_function(self, func_name, func):
        self.functions[func_name] = func

    def set_socket_manager(self, socket_manager):
        self.socket_manager = socket_manager
 
    async def handle_client_for_function(self, sid, data):
        func_name = data.get('func_name', None)
        args = data.get('args', [])
 
        if func_name and func_name in self.functions:
            if args:  # Check if arguments are present
                # You can use asyncio.Queue to manage the asynchronous results
                result_queue = Queue()
                # Create an event to signal when the task is completed
                task_completed = Event()
 
                # Define a coroutine to execute the function
                async def execute_function():
                    try:
                        func = self.functions[func_name]
                        if asyncio.iscoroutinefunction(func):
                            result = await func(*args)  # Await the coroutine function
                        else:
                            result = func(*args)  # Call regular or lambda function
                        await asyncio.sleep(0)  # Allows other tasks to run in case this one is blocking
                        result_queue.put(result)
                    except Exception as e:
                        result_queue.put(str(e))  # Convert exception to a string for JSON serialization
                    finally:
                        task_completed.set()  # Signal that the task is completed
 
                # Create the asyncio task for executing the function
                asyncio.create_task(execute_function())
 
                # Wait for the task to complete
                await asyncio.to_thread(task_completed.wait)
 
                # Retrieve the result from the queue
                result = result_queue.get()
 
                # Emit the response to the client using the appropriate method (e.g., socket_manager.emit)
                # Note: Replace 'self.socket_manager.emit' with the actual method you use to emit responses.
                # This method may vary depending on the library or framework you are using for socket handling.
                await self.socket_manager.emit('response', result, room=sid)
            else:
                # If no arguments are present, simply call the function without passing any arguments
                result = self.functions[func_name]()
                await self.socket_manager.emit('response', result, room=sid)
 
    def register_class(self, class_name, class_instance):
        self.classes[class_name] = class_instance
 
    async def handle_client_for_method(self, sid, data):
        class_name = data.get('class_name', None)
        method_name = data.get('method_name', None)
        args = data.get('args', [])
 
        if class_name and method_name:
            if class_name in self.classes:
                class_instance = self.classes[class_name]
                method = getattr(class_instance, method_name, None)
                if method and callable(method):
                    if args:  # Check if arguments are present
                        # You can use asyncio.Queue to manage the asynchronous results
                        result_queue = Queue()
                        # Create an event to signal when the task is completed
                        task_completed = Event()
 
                        # Define a coroutine to execute the method
                        async def execute_method():
                            try:
                                result = method(*args)
                                await asyncio.sleep(0)  # Allows other tasks to run in case this one is blocking
                                result_queue.put(result)
                            except Exception as e:
                                result_queue.put(str(e))  # Convert exception to a string for JSON serialization
                            finally:
                                task_completed.set()  # Signal that the task is completed
 
                        # Create the asyncio task for executing the method
                        asyncio.create_task(execute_method())
 
                        # Wait for the task to complete
                        await asyncio.to_thread(task_completed.wait)
 
                        # Retrieve the result from the queue
                        result = result_queue.get()
 
                        # Emit the response to the client using the appropriate method (e.g., self.socket_manager.emit)
                        # Note: Replace 'self.socket_manager.emit' with the actual method you use to emit responses.
                        # This method may vary depending on the library or framework you are using for socket handling.
                        await self.socket_manager.emit('response', result, room=sid)
                    else:
                        # If no arguments are present, simply call the method without passing any arguments
                        result = method()
                        await self.socket_manager.emit('response', result, room=sid)
                else:
                    raise RuntimeError(f"Method '{method_name}' not found in class '{class_name}'.")
            else:
                raise RuntimeError(f"Class '{class_name}' not found.")
        else:
            raise RuntimeError("Invalid data received from the client.")





event = EventListener()