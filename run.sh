OUTPUT_FILE="data/legitng_english.jsonl"
LINE_COUNT=0
touch $OUTPUT_FILE

is_running() {
    read NEW_LINE_COUNT < <(wc -l < $OUTPUT_FILE)
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
        # https://www.educba.com/linux-kill-signals/
        kill -2 $pid
        read pid < <(run_spider)
    fi

    sleep 300
done
