import {Pool,spawn,Worker} from "threads";

const pool = Pool(
    ()=>{spawn(new Worker("./worker"))},4
)

async function run(){
    const result = await Promise.all(
        pool.queue(worker=>{
            worker.getChunk()
        })
    )
}

run().then(()=>pool.terminate());