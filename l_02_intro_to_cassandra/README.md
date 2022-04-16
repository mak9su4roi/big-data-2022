# Lab II: Introduction to cassandra


### Requirements
- bash
- docker


### Setup
-   ```bash
    git clone https://github.com/mak9su4roi/big-data-2022
    ```
-   ```bash
    chmod -R +x ./big-data-2022/l_02_intro_to_cassandra/
    ```
-   ```bash
    cd ./big-data-2022/l_02_intro_to_cassandra
    ```

### Without docker-compose
-   ```bash
    ./run-cluster.sh
    ```
    ![](./media/0.0.png)
-   ```bash
    ./ddl.sh
    ```
    ![](./media/0.1.png)
-   ```bash
    ./dml.sh
    ```
    ![](./media/0.2.png)
-   ```bash
    ./shutdown-cluster.sh
    ```
    ![](./media/0.3.png)

### With docker-compose
-   ```bash
    docker-compose up -d n{1..3}
    ```
    ![](./media/1.0.png)
-   ```bash
    ./ddl.sh
    ```
    ![](./media/1.1.png)
-   ```bash
    ./dml.sh
    ```
    ![](./media/1.2.png)
-   ```bash
    docker-compose down
    ```
    ![](./media/1.3.png)
