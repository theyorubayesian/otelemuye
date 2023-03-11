OUTPUT_FILE="data/complete_legitng_hausa.jsonl"
LINE_COUNT=0

is_running() {
    read NEW_LINE_COUNT file < <(wc -l < $OUTPUT_FILE)
    [[ $NEW_LINE_COUNT -gt $LINE_COUNT ]] && echo "true $NEW_LINE_COUNT" || echo "false $NEW_LINE_COUNT"
}

run_spider() {
    scrapy crawl legitng_spider -s JOBDIR=crawls/legitng_spider &
    echo $!
}

read pid < <(run_spider)

while true;
do
    read running LINE_COUNT < <(is_running)
    if $running; then
        :
    else
        kill -9 $pid
        read pid < <(run_spider)
        pid=$1
    fi

    sleep 300
done
