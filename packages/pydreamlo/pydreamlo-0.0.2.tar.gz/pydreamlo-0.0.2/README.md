# PYDREAMLO
Simple,free and easy-to-use Leader Board system using https://dreamlo.com.

### Install
- Use pip to install
  ```bash
    $ pip install pydreamlo
    ```
    
    or
    
    ```bash
    $ pip3 install pydreamlo
    ```
    
    or
    
    ```bash
    $ python -m pip install pydreamlo
    ```
- or Build from source
- or Copy the `src/pydreamlo` folder to your project directory and import it.
### Usage:
- Create a dreamlo url by going to https://dreamlo.com
For using this LeaderBoard you need 2 `url`s (`private dreamlo url` and `public dreamplo url`)

    - Creating the `url`s
        - `private url` : copy the `private-key` given by dreamlo and join it with the url.(the protocol may be different)
          
            ```python
            pr_key = "http://dreamlo.com/{your_private_key}"
            ```
            
        - `private url` : copy the `public-key` given by dreamlo and join it with the url.(the protocol may be different)
          
            ```python
            pu_key = "http://dreamlo.com/{your_public_key}"
            ```
            
- Use `dreamlopy` to work with your leader board. 
    ```python
    from pydreamlo import LeaderBoard
    pr_key = "http://dreamlo.com/{your_private_key}"
    pu_key = "http://dreamlo.com/{your_public_key}"

    cool_leader_board = LeaderBoard(pr_key,pu_key)
    ```
    The module `dreamlopy` is initialized,now you use the methods in the module to perform the operations.
    
    - `.add(username,score,time,text)`

        `add()` is used to add a new user to the leader board. `username` and `score` are necessary parameters.The `time` is the time taken to finish.(Sorting based on time is available)
        ```python
        cool_leader_board.add("some-user",100,10,"user is cool")
        ```
        returns a string "OK" if sucessful
    - `.delete(username)`

        `delete()` is used to delete a specific user from the leaderboard.`username` is the only parameter(Note:only one user can have a specific username)
        ```python
        cool_leader_board.delete("some-user")
        ```
    - `.clear()`

        `clear()` is used to clear the entire leaderboard.
        ```python
        cool_leader_board.clear()
        ```
    - `.get(index:int = 0,upto:int = 0,rtype:str = 'json',sort:str='')`
        
        used to get the leaderboard data.
        - `index` defines the index from where should the results start showing.(default is 0)
        - `upto` defines the number of users to return after the index.(default is 0,so it will return the entire leaderboard)
        - `rtype` defines the return type of the `get` method.
            - `rtype = "json"`
            - `rtype = "xml"`
            - `rtype = "pipe"`
            - `rtype = "quote"`
        - `sort` is an additional command return the sorted leaderboard based on `time` taken by the user
            - `sort='a'` for ascending(less time first)
            - `sort='d'` for descending(greter time first)
            ```python
            """
            This will return all the leaderboard data starting from index 0 to (index 0 + next 50 spaces) and will return as a "json" and arranges the leaderboard based on time(the user with less time shows at first).
            """
            cool_leader_board.get(0,50,"json",'a')
            ```
    - `.get_new_sorted(index:int = 0,upto:int = 0,rtype:str = 'json',sort:str='')`

        used to retrieve the leaderboard with respect to time score's was added.(same parameter as `.get()`)
    - `.get_user(username,rtype)`

        used to get deatils of a specific user.
