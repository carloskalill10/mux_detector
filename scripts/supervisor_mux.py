#!/usr/bin/env python
import rospy
from geometry_msgs.msg import Twist
from std_msgs.msg import Bool

class PlannerMux:
    def __init__(self):
        rospy.init_node('planner_supervisor_mux')
        
        self.use_teb = False # Por padrao assume o FSMT (estatico)
        
        # topico do comando final para o jackal
        self.cmd_pub = rospy.Publisher('/jackal_velocity_controller/cmd_vel', Twist, queue_size=1)
        
        # escuta se tem obstaculo dinamico
        rospy.Subscriber('/has_dynamic_obstacles', Bool, self.status_callback)
        
        # escuta os dois algoritmos
        rospy.Subscriber('/teb/cmd_vel', Twist, self.teb_callback)
        rospy.Subscriber('/fsmt/cmd_vel', Twist, self.fsmt_callback)
        
        rospy.loginfo("MUX iniciado. Controle atual: FSMT (Estatico)")

    def status_callback(self, msg):
        # Se o status mudar avisa no terminal
        if self.use_teb != msg.data:             
            self.use_teb = msg.data

    def teb_callback(self, msg):
        # Se o mux disse que tem dinamico, passa o comando do TEB
        if self.use_teb:
            self.cmd_pub.publish(msg)
            rospy.logwarn("ALERTA: Obstaculo dinamico! TEB controlando")

    def fsmt_callback(self, msg):
        # Se o mux disse que NAO tem dinamico, passa o comando do FSMT adiante
        if not self.use_teb:
            self.cmd_pub.publish(msg)
            rospy.loginfo(" FSMT controlando.")

if __name__ == '__main__':
    try:
        mux = PlannerMux()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass