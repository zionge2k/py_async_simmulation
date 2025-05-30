import asyncio
import random

# 전역 재고 변수
stock = 0
# 재고 접근을 위한 Lock (뮤텍스)
stock_lock = asyncio.Lock()
# 구매 성공한 사용자 수
successful_purchases = 0
# 구매 요청 큐 (FIFO 순서 보장)
purchase_queue = asyncio.Queue()


async def replenish_stock():
    """일정 시간마다 재고를 보충하는 작업"""
    global stock
    
    while True:
        # 1-3초 마다 재고 보충
        await asyncio.sleep(random.uniform(1, 3))
        
        async with stock_lock:
            # 10-30개의 재고 추가
            add_amount = random.randint(10, 30)
            stock += add_amount
            print(f"📦 재고 보충: +{add_amount}개 (현재 재고: {stock}개)")


async def purchase_worker():
    """큐에서 구매 요청을 순서대로 처리하는 워커"""
    global stock, successful_purchases
    
    while True:
        # 큐에서 고객 정보 가져오기 (FIFO)
        customer_id = await purchase_queue.get()
        
        if customer_id is None:
            purchase_queue.task_done()
            break
        
        print(f"👤 고객 #{customer_id} 구매 처리 중...")
        
        async with stock_lock:
            if stock > 0:
                # 재고가 있으면 구매 성공
                stock -= 1
                successful_purchases += 1
                print(f"✅ 고객 #{customer_id} 구매 성공! (남은 재고: {stock}개)")
                success = True
            else:
                # 재고가 없으면 구매 실패
                print(f"❌ 고객 #{customer_id} 구매 실패 - 재고 없음")
                success = False
        
        # 작업 완료 표시
        purchase_queue.task_done()


async def customer_request(customer_id: int):
    """고객이 구매를 요청하는 작업"""
    # 고객마다 랜덤한 시간에 쇼핑몰 방문
    await asyncio.sleep(random.uniform(0, 5))
    
    print(f"🔔 고객 #{customer_id} 구매 요청 (큐에 추가)")
    
    # 구매 요청을 큐에 추가 (순서 보장)
    await purchase_queue.put(customer_id)


async def main():
    """메인 실행 함수"""
    global stock
    
    print("🛒 쇼핑몰 시뮬레이션 시작!")
    print("📌 Queue를 사용한 순서 보장 버전\n")
    
    # 초기 재고 설정
    stock = 20
    print(f"초기 재고: {stock}개")
    
    # 고객 수 설정 (10-100명)
    num_customers = random.randint(10, 100)
    print(f"총 고객 수: {num_customers}명\n")
    
    # 재고 보충 작업 시작
    replenish_task = asyncio.create_task(replenish_stock())
    
    # 구매 처리 워커 시작 (순서대로 처리)
    worker_task = asyncio.create_task(purchase_worker())
    
    # 고객 요청 작업들 생성
    customer_tasks = [
        asyncio.create_task(customer_request(i))
        for i in range(1, num_customers + 1)
    ]
    
    # 모든 고객의 요청이 끝날 때까지 대기
    await asyncio.gather(*customer_tasks)
    
    # 모든 큐 작업이 처리될 때까지 대기
    await purchase_queue.join()
    
    # 워커 종료 신호 전송
    await purchase_queue.put(None)
    # 워카가 완전히 종료될 때까지 대기 모든 정리 작업 완료 보장
    await worker_task
    
    # 재고 보충 작업 취소
    replenish_task.cancel()
    
    # 결과 출력
    print(f"\n📊 시뮬레이션 결과:")
    print(f"총 고객 수: {num_customers}명")
    print(f"구매 성공: {successful_purchases}명")
    print(f"구매 실패: {num_customers - successful_purchases}명")
    print(f"최종 재고: {stock}개")


if __name__ == "__main__":
    asyncio.run(main()) 