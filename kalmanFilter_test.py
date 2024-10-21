#ダミーデータで位置，速度，加速度のカルマンフィルタの精度を検証するのに使っていた
#パラメータQやRをいじることで精度を上げていた


#import matplotlib
#matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
T=[]
dt = 0.1
def kalman_filter(A, B, H, Q, R, x0, P0, measurements):
    n = A.shape[0] # 状態ベクトルの次元
    m = len(measurements) # 観測の回数

    # 初期化
    x = x0
    P = P0
    t = 0
    filtered_states = []
    prediction_states = [[0, 0, 0, 0, 0, 0],[0,0,0,0,0,0],[0,0,0,0,0,0]]

    for i in range(m):
        # 予測ステップ
        x_hat = np.dot(A, x)
        P_hat = np.dot(np.dot(A, P), A.T) + Q

        # カルマンゲインの計算
        K = np.dot(np.dot(P_hat, H.T), np.linalg.inv(np.dot(np.dot(H, P_hat), H.T) + R))

        # 観測更新ステップ
        z = measurements[i]
        x = x_hat + np.dot(K, z - np.dot(H, x_hat))
        P = P_hat - np.dot(np.dot(K, H), P_hat)
        
        #print(z)
        #print(np.dot(H, x_hat))
        #print(z - np.dot(H, x_hat))

        t=t+dt

        #3期先予測ステップ
        h_pre3 = np.dot(A,(np.dot(A,(np.dot(A, x)))))

        prediction_states.append(h_pre3)
        filtered_states.append(x)
        T.append(t)

    #prediction_states = np.delete(prediction_states, -1)
    filtered_states.append(x)  
    filtered_states.append(x)
    filtered_states.append(x)  #prediction_statesだけ3つ要素が多いので前回と同じ推定値を追加
    T.append(t+dt)
    T.append(t+dt)
    T.append(t+dt)
    #print(filtered_states)
    return np.array(filtered_states), np.array(prediction_states), np.array(T)
    


# システム行列
A = np.array([[1, 1*dt, 0.5*dt*dt, 0, 0, 0],
              [0, 1, 1*dt, 0, 0, 0],
              [0, 0, 1, 0, 0, 0],
              [0, 0, 0, 1, 1*dt, 0.5*dt*dt],
              [0, 0, 0, 0, 1, 1*dt],
              [0, 0, 0, 0, 0, 1]])

B = np.zeros((6, 1))

# 観測行列 (x座標とy座標のみを観測)
H = np.array([[1, 0, 0, 0, 0, 0],
              [0, 0, 0, 1, 0, 0]])

# プロセスノイズ共分散行列
Q = np.eye(6) * 0.03

# 観測ノイズ共分散行列
#R = np.eye(2) * 0
R = np.array([[0.09, 0],
              [0, 0.07]])

# 初期状態推定
x0 = np.array([0, 0, 0, 0, 0, 0])
P0 = np.eye(6)

# ダミーの観測データ
measurements = np.array([[1, 2], [2, 3], [3, 4], [4, 5], [5, 6], [6, 7], [6, 8],[6,9],[5,10],[4,11],[3,12],[2,13], [1, 14],[0,15],[-1,16],[-2,17],[-1,18],[1,19],[3,20],[5,21],[7,22],[9,23],[11,24],[13,25]])
#下はゆっくり
measurements = np.array([[703.1877256317689, 477.1913357400722], [722.992125984252, 482.50787401574803], [745.9694323144105, 485.1965065502183], [762.3625954198474, 497.1832061068702], [782.0190839694657, 498.3358778625954], [791.5533596837945, 494.84584980237156], [813.9928057553957, 497.9640287769784], [824.8624535315985, 496.6208178438662], [826.985401459854, 508.036496350365], [824.2350993377484, 501.77814569536423], [820.1348684210526, 496.4144736842105], [805.2007042253521, 493.91901408450707], [779.9776951672862, 491.4944237918216], [765.2868217054264, 484.87984496124034], [754.8099173553719, 489.10330578512395], [732.2526315789473, 478.41052631578947], [722.8583690987125, 483.84120171673817], [699.59375, 480.62109375], [685.942084942085, 475.5405405405405], [674.1122807017543, 472.19649122807016], [652.55938697318, 470.3103448275862], [642.5254901960784, 474.678431372549], [631.8192307692308, 475.5153846153846], [620.8120805369127, 470.744966442953], [601.992565055762, 479.52416356877325], [589.2209737827716, 481.83895131086143], [578.8985507246376, 482.8768115942029], [556.8625429553265, 484.30584192439864], [546.5548172757475, 483.2126245847176], [534.5723905723905, 489.4074074074074], [510.59027777777777, 496.12847222222223], [497.7821782178218, 503.1122112211221], [488.4828660436137, 505.97196261682245], [469.06060606060606, 514.9779614325068], [460.84180790960454, 520.1101694915254], [452.93654822335026, 526.4720812182741], [444.8765743073048, 532.4937027707808], [441.65034965034965, 530.5804195804196], [441.26356589147287, 535.062015503876], [447.0, 525.6594202898551], [454.25897435897434, 527.0410256410256], [464.7091836734694, 526.3392857142857], [480.6806282722513, 515.0942408376964], [490.38964577656674, 513.0899182561308], [500.61764705882354, 512.1323529411765], [521.3443113772455, 504.08682634730536], [533.1101694915254, 496.638418079096], [546.9049079754601, 498.62883435582825], [558.9335347432025, 491.0453172205438], [581.421052631579, 486.31907894736844], [596.0809061488674, 486.62783171521033], [608.0185185185185, 489.0888888888889], [623.09, 482.44], [648.8925925925926, 482.3740740740741], [665.9077490774907, 485.2361623616236], [679.1793893129772, 485.35114503816794], [705.8795620437957, 483.64963503649636], [725.3971631205674, 487.9148936170213], [738.3745173745174, 484.6949806949807], [764.1280991735537, 492.9710743801653], [776.5912408759124, 499.14963503649636], [783.3390557939914, 495.90557939914163], [801.5525423728814, 495.8915254237288], [806.9180327868852, 500.3196721311475], [815.685606060606, 501.43939393939394], [821.5733788395904, 502.6928327645051], [819.886287625418, 509.8695652173913], [816.01393728223, 504.2229965156794], [807.7607973421927, 505.06644518272424], [788.5206611570248, 504.6735537190083], [774.0294117647059, 492.3860294117647], [764.1328413284133, 493.06642066420665], [736.8858267716536, 492.21259842519686], [721.9694656488549, 483.09923664122135], [711.035019455253, 488.38132295719845], [698.9516129032259, 483.9717741935484], [677.1111111111111, 486.4102564102564], [667.3898305084746, 479.5220338983051], [653.0876494023904, 483.0756972111554], [627.2991803278688, 485.422131147541], [618.19, 484.32666666666665], [603.1953125, 489.10546875], [590.1624548736462, 491.4945848375451], [571.6979166666666, 497.99305555555554], [562.2816901408451, 503.88380281690144], [552.8636363636364, 503.77272727272725], [546.8993288590603, 504.8724832214765], [531.2484472049689, 506.35403726708074]])
#下は早め
#measurements = np.array([[725.9484978540772, 498.9442060085837], [725.7795918367347, 498.39591836734695], [724.4501992031873, 501.7410358565737], [725.5052631578948, 498.2456140350877], [722.665306122449, 498.0040816326531], [724.2649006622516, 490.2913907284768], [719.6765676567657, 495.12541254125415], [718.4109589041096, 495.79794520547944], [699.8350168350169, 493.6531986531987], [684.4590163934427, 490.1213114754098], [638.992565055762, 477.2007434944238], [605.6293103448276, 473.14224137931035], [574.4117647058823, 476.83193277310926], [541.4952830188679, 493.8679245283019], [546.6870229007634, 482.53053435114504], [572.9032258064516, 475.0483870967742], [590.425925925926, 472.12654320987656], [607.1018518518518, 467.679012345679], [626.8823529411765, 462.32026143790847], [670.9673202614379, 456.4281045751634], [694.911196911197, 462.019305019305]])
#print(measurements)

# カルマンフィルタの実行
filtered_states, prediction_states, T = kalman_filter(A, B, H, Q, R, x0, P0, measurements)
#measurements = np.append(measurements,[0,0], axis=0)
#prediction_statesだけ3つ要素が多いので0,0を追加
measurements = np.vstack([measurements, np.array([0, 0])])
measurements = np.vstack([measurements, np.array([0, 0])])
measurements = np.vstack([measurements, np.array([0, 0])])

# 結果の表示
#print(filtered_states)
#print(prediction_states)


filtered_states_x = filtered_states[:, 0]
prediction_states_x = prediction_states[:, 0]
print(type(filtered_states))  #np.ndarray
print(type(measurements[0]))


plt.plot(T,filtered_states_x, 'o', color='red', linewidth=1.0, label='Estimation')
plt.plot(T,measurements[:,0], '*',color='green',label='Obvervation')
plt.plot(T,prediction_states_x, '*',color='blue',label='Prediction')
# plt.errorbar(T,XT, yerr=XTERR, capsize=5, fmt='o', color='red', ecolor='orange',label='Estimate')
plt.xlabel('T')
plt.ylabel('X')
plt.grid(True)
plt.legend()
plt.show()
plt.savefig('figure03.jpg')

